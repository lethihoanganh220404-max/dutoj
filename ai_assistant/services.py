"""Luu bai do AI sinh ra vao database, theo dung cach import_problems.py lam."""

import json
import re

from django.db import transaction

from judge.models import Language, Problem, ProblemGroup, ProblemType, Profile


class LoiLuuBai(Exception):
    """Loi khi luu bai. Bat rieng de hien thong bao de hieu."""


def tach_ten_bai(markdown):
    """Lay ten bai tu dong tieu de dau tien (# Ten bai)."""
    for dong in markdown.splitlines():
        dong = dong.strip()
        if dong.startswith('# '):
            return dong[2:].strip()
    return ''


def lam_sach_ma(ma):
    """Ma bai chi duoc chua chu thuong, so va dau gach duoi."""
    ma = (ma or '').strip().lower()
    return re.sub(r'[^a-z0-9_]', '', ma)


@transaction.atomic
def luu_bai(ma, ten, mo_ta, time_limit, memory_limit, points, nguoi_dung):
    ma = lam_sach_ma(ma)
    if not ma:
        raise LoiLuuBai('Ma bai khong hop le. Chi dung chu thuong, so, gach duoi.')
    if not ten.strip():
        raise LoiLuuBai('Chua co ten bai.')
    if Problem.objects.filter(code=ma).exists():
        raise LoiLuuBai('Ma bai "%s" da ton tai. Doi ma khac.' % ma)

    group, _ = ProblemGroup.objects.get_or_create(
        name='ai-generated', defaults={'full_name': 'AI Generated'},
    )
    ptype, _ = ProblemType.objects.get_or_create(
        name='uncategorized', defaults={'full_name': 'Uncategorized'},
    )

    bai = Problem(
        code=ma,
        name=ten.strip(),
        description=mo_ta,
        time_limit=time_limit,
        memory_limit=memory_limit,
        points=points,
        partial=False,
        group=group,
        is_public=False,   # an di vi chua co test case
    )
    bai.save()

    bai.types.set([ptype])
    bai.allowed_languages.set(list(Language.objects.all()))

    profile = Profile.objects.filter(user=nguoi_dung).first()
    if profile:
        bai.authors.set([profile])

    return bai


def _tach_json(van_ban):
    """AI doi khi boc ket qua trong ```json ... ```. Go bo lop bao do."""
    import json
    import re

    s = van_ban.strip()
    s = re.sub(r'^```(?:json)?\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    # Cat lay phan tu dau ngoac nhon dau den dau ngoac nhon cuoi.
    dau, cuoi = s.find('{'), s.rfind('}')
    if dau != -1 and cuoi != -1:
        s = s[dau:cuoi + 1]

    for lan in range(2):
        try:
            return json.loads(s)
        except ValueError:
            if lan:
                break
            # AI hay viet LaTeX kieu \le thang vao JSON, ma trong JSON
            # dau \ phai viet doi. Nhan doi nhung dau \ khong hop le.
            s = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)

    raise LoiLuuBai('AI khong tra ve JSON hop le:\n' + s[:400])


def sinh_goi_y(problem, bat_buoc_goi_lai=False):
    """Sinh goi y 3 muc cho mot bai.

    Da co trong DB thi lay ra luon, khong goi API - tru khi
    bat_buoc_goi_lai=True.
    """
    from .llm_client import MODEL, goi_llm
    from .models import GoiY
    from .prompts import SINH_GOI_Y

    cu = GoiY.objects.filter(problem=problem).first()
    if cu and not bat_buoc_goi_lai:
        return cu, False   # False = lay tu cache, khong ton luot API

    van_ban = goi_llm(SINH_GOI_Y % problem.description)
    du_lieu = _tach_json(van_ban)

    goi_y, _ = GoiY.objects.update_or_create(
        problem=problem,
        defaults={
            'muc1': du_lieu.get('muc1', ''),
            'muc2': du_lieu.get('muc2', ''),
            'muc3': du_lieu.get('muc3', ''),
            'mo_hinh': MODEL,
        },
    )
    return goi_y, True   # True = vua goi API


def _tach_gen_sol(van_ban):
    """Tach GENERATOR, SOLVER va SOLVER2 tu cau tra loi cua AI."""
    import re

    s = van_ban.replace('```python', '').replace('```', '')

    # Co phai bai da dap an khong? AI tu bao.
    da_dap_an = ''
    k_dd = re.search(r'===\s*DA_DAP_AN\s*===(.*?)===\s*GENERATOR\s*===',
                     s, re.S | re.I)
    if k_dd:
        da_dap_an = k_dd.group(1).strip()

    # Co du ca 4 phan: generator, solver, solver2, checker
    khop = re.search(
        r'===\s*GENERATOR\s*===(.*?)'
        r'===\s*SOLVER\s*===(.*?)'
        r'===\s*SOLVER2\s*===(.*?)'
        r'===\s*CHECKER\s*===(.*)',
        s, re.S | re.I,
    )
    if khop:
        checker = khop.group(4).strip()
        if 'def check(' not in checker:
            checker = ''        # AI viet "KHONG CAN" hoac bo trong
        return (khop.group(1).strip(), khop.group(2).strip(),
                khop.group(3).strip(), da_dap_an, checker)

    khop = re.search(
        r'===\s*GENERATOR\s*===(.*?)'
        r'===\s*SOLVER\s*===(.*?)'
        r'===\s*SOLVER2\s*===(.*)',
        s, re.S | re.I,
    )
    if khop:
        return (khop.group(1).strip(), khop.group(2).strip(),
                khop.group(3).strip(), da_dap_an, '')

    # AI chi viet mot solver: van chap nhan, nhung khong kiem chung cheo duoc.
    khop = re.search(
        r'===\s*GENERATOR\s*===(.*?)===\s*SOLVER\s*===(.*)',
        s, re.S | re.I,
    )
    if khop:
        return khop.group(1).strip(), khop.group(2).strip(), '', da_dap_an, ''

    raise LoiLuuBai(
        'AI khong tra ve dung dinh dang GENERATOR/SOLVER:\n' + s[:400]
    )


def sinh_test_case(problem, so_test=15):
    """Sinh test case that: AI viet generator + solver, MAY chay de lay output.

    Khong bao AI tu nghi cap input/output - no tinh nham. Chi bao no viet
    code, roi chay code do de lay ket qua dung.
    """
    import os
    import tempfile

    from .models import TestCaseNhap
    from .llm_client import goi_llm
    from .prompts import SINH_TEST_CASE
    from .sandbox import LoiChayCode, chay_python

    van_ban = goi_llm(SINH_TEST_CASE % problem.description)
    gen_code, sol_code, sol2_code, da_dap_an, checker_code = _tach_gen_sol(van_ban)

    cac_test = []
    so_lan_hong = 0
    so_lan_lech = 0      # hai solver cho ket qua khac nhau

    with tempfile.TemporaryDirectory() as tam:
        duong_gen = os.path.join(tam, 'gen.py')
        duong_sol = os.path.join(tam, 'sol.py')
        duong_sol2 = os.path.join(tam, 'sol2.py')
        open(duong_gen, 'w').write(gen_code)
        open(duong_sol, 'w').write(sol_code)
        if sol2_code:
            open(duong_sol2, 'w').write(sol2_code)

        # Chia test theo kich thuoc: nho (bien), vua, lon (sat gioi han tren).
        # Test lon moi la thu loc duoc loi giai cham.
        so_nho = max(2, so_test // 5)
        so_lon = max(2, so_test // 5)
        so_vua = so_test - so_nho - so_lon
        ke_hoach = (['nho'] * so_nho + ['vua'] * so_vua + ['lon'] * so_lon)

        for muc in ke_hoach:
            # Test lon duoc chay lau hon vi solver Python cham.
            giay = 30 if muc == 'lon' else 10
            for _ in range(3):          # moi test thu toi da 3 lan
                try:
                    dau_vao = chay_python(duong_gen, thu_muc=tam,
                                          tham_so=[muc], giay=giay)
                    if not dau_vao.strip():
                        so_lan_hong += 1
                        continue
                    dau_ra = chay_python(duong_sol, dau_vao=dau_vao,
                                         thu_muc=tam, giay=giay)
                    if not dau_ra.strip():
                        so_lan_hong += 1
                        continue

                    # Kiem chung cheo: chay solver thu hai, phai ra giong nhau.
                    # Neu lech thi mot trong hai hieu sai de - bo test nay.
                    if sol2_code:
                        try:
                            dau_ra2 = chay_python(duong_sol2, dau_vao=dau_vao,
                                                  thu_muc=tam, giay=giay)
                        except LoiChayCode:
                            so_lan_hong += 1
                            continue
                        if dau_ra.split() != dau_ra2.split():
                            so_lan_lech += 1
                            continue

                    cac_test.append((dau_vao, dau_ra))
                    break
                except LoiChayCode:
                    so_lan_hong += 1

    if so_lan_lech:
        raise LoiLuuBai(
            'Hai loi giai tham chieu cho ket qua KHAC NHAU tren %d lan thu. '
            'Nghia la it nhat mot trong hai hieu sai de bai, khong the tin '
            'test case sinh ra. Hay sinh lai, hoac kiem tra lai de bai.'
            % so_lan_lech
        )

    if len(cac_test) < 5:
        raise LoiLuuBai(
            'Chi sinh duoc %d test hop le (hong %d lan). '
            'Code AI viet co van de - thu sinh lai.'
            % (len(cac_test), so_lan_hong)
        )

    # KHONG ghi thang vao /problems. Luu nhap de nguoi duyet truoc.
    nhap, _ = TestCaseNhap.objects.update_or_create(
        problem=problem,
        defaults={
            'generator': gen_code,
            'solver': sol_code + (
                '\n\n# ===== LOI GIAI THAM CHIEU THU HAI (kiem chung cheo) =====\n'
                + sol2_code if sol2_code else ''
            ),
            'du_lieu': json.dumps(cac_test),
            'so_test': len(cac_test),
            'so_lan_hong': so_lan_hong,
            'da_dap_an': da_dap_an,
            'checker': checker_code,
            'da_duyet': False,
        },
    )

    return {
        'nhap_id': nhap.id,
        'so_test': len(cac_test),
        'so_lan_hong': so_lan_hong,
        'test_mau': cac_test[:3],
    }


def ghi_test_case(nhap):
    """Nguoi da duyet: ghi tu ban nhap ra thu muc /problems that."""
    import os

    from django.conf import settings

    cac_test = json.loads(nhap.du_lieu)
    if not cac_test:
        raise LoiLuuBai('Ban nhap khong co test nao.')

    goc = getattr(settings, 'DMOJ_PROBLEM_DATA_ROOT', '/problems')
    thu_muc_bai = os.path.join(str(goc), nhap.problem.code)
    os.makedirs(thu_muc_bai, exist_ok=True)

    # Xoa test cu de khong lan lon voi test moi.
    for ten in os.listdir(thu_muc_bai):
        if ten.endswith('.in') or ten.endswith('.out'):
            os.remove(os.path.join(thu_muc_bai, ten))

    n = len(cac_test)
    chia, du = divmod(100, n)

    for k, (dau_vao, dau_ra) in enumerate(cac_test, start=1):
        open(os.path.join(thu_muc_bai, '%02d.in' % k), 'w').write(dau_vao)
        open(os.path.join(thu_muc_bai, '%02d.out' % k), 'w').write(dau_ra)

    with open(os.path.join(thu_muc_bai, 'init.yml'), 'w') as f:
        # Co special judge thi khai bao, may cham se goi thay vi so sanh van ban.
        if nhap.checker:
            f.write('checker:\n')
            f.write('  name: bridged\n')
            f.write('  args:\n')
            f.write('    files: checker.py\n')
            f.write('    lang: PY3\n')
            f.write('    type: default\n')
        f.write('test_cases:\n')
        for k in range(1, n + 1):
            diem = chia + (1 if k <= du else 0)
            f.write('- in: %02d.in\n  out: %02d.out\n  points: %d\n'
                    % (k, k, diem))

    if nhap.checker:
        open(os.path.join(thu_muc_bai, 'checker.py'), 'w').write(nhap.checker)

    open(os.path.join(thu_muc_bai, '_generator.py'), 'w').write(nhap.generator)
    open(os.path.join(thu_muc_bai, '_solver.py'), 'w').write(nhap.solver)

    nhap.da_duyet = True
    nhap.save()

    return {'so_test': n, 'thu_muc': thu_muc_bai}


def sinh_checker(nhap):
    """Sinh special judge cho bai da dap an, dua tren ban nhap da co."""
    from .llm_client import goi_llm
    from .prompts import SINH_CHECKER

    cac_test = json.loads(nhap.du_lieu or '[]')
    if not cac_test:
        raise LoiLuuBai('Chua co test nao de lam mau cho checker.')

    vao_mau, ra_mau = cac_test[0]

    van_ban = goi_llm(SINH_CHECKER % (
        nhap.problem.description, vao_mau[:2000], ra_mau[:1000],
    ))

    code = van_ban.replace('```python', '').replace('```', '').strip()
    if 'def check(' not in code:
        raise LoiLuuBai('AI khong viet ra ham check():\n' + code[:400])

    nhap.checker = code
    nhap.save()
    return code
