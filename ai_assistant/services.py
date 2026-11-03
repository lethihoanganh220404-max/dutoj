"""Luu bai do AI sinh ra vao database, theo dung cach import_problems.py lam."""

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
    """Tach phan GENERATOR va SOLVER tu cau tra loi cua AI."""
    import re

    s = van_ban.replace('```python', '').replace('```', '')
    khop = re.search(
        r'===\s*GENERATOR\s*===(.*?)===\s*SOLVER\s*===(.*)',
        s, re.S | re.I,
    )
    if not khop:
        raise LoiLuuBai(
            'AI khong tra ve dung dinh dang GENERATOR/SOLVER:\n' + s[:400]
        )
    return khop.group(1).strip(), khop.group(2).strip()


def sinh_test_case(problem, so_test=15):
    """Sinh test case that: AI viet generator + solver, MAY chay de lay output.

    Khong bao AI tu nghi cap input/output - no tinh nham. Chi bao no viet
    code, roi chay code do de lay ket qua dung.
    """
    import os
    import tempfile

    from django.conf import settings

    from .llm_client import goi_llm
    from .prompts import SINH_TEST_CASE
    from .sandbox import LoiChayCode, chay_python

    van_ban = goi_llm(SINH_TEST_CASE % problem.description)
    gen_code, sol_code = _tach_gen_sol(van_ban)

    cac_test = []
    so_lan_hong = 0

    with tempfile.TemporaryDirectory() as tam:
        duong_gen = os.path.join(tam, 'gen.py')
        duong_sol = os.path.join(tam, 'sol.py')
        open(duong_gen, 'w').write(gen_code)
        open(duong_sol, 'w').write(sol_code)

        # Chay nhieu hon so can, vi mot so lan se hong.
        for _ in range(so_test * 2):
            if len(cac_test) >= so_test:
                break
            try:
                dau_vao = chay_python(duong_gen, thu_muc=tam)
                if not dau_vao.strip():
                    so_lan_hong += 1
                    continue
                dau_ra = chay_python(duong_sol, dau_vao=dau_vao, thu_muc=tam)
                if not dau_ra.strip():
                    so_lan_hong += 1
                    continue
                cac_test.append((dau_vao, dau_ra))
            except LoiChayCode:
                so_lan_hong += 1

    if len(cac_test) < 5:
        raise LoiLuuBai(
            'Chi sinh duoc %d test hop le (hong %d lan). '
            'Code AI viet co van de - thu sinh lai.'
            % (len(cac_test), so_lan_hong)
        )

    # Ghi ra thu muc problem_data theo dung chuan DMOJ.
    goc = getattr(settings, 'DMOJ_PROBLEM_DATA_ROOT', '/problems')
    thu_muc_bai = os.path.join(str(goc), problem.code)
    os.makedirs(thu_muc_bai, exist_ok=True)

    n = len(cac_test)
    chia, du = divmod(100, n)

    for k, (dau_vao, dau_ra) in enumerate(cac_test, start=1):
        open(os.path.join(thu_muc_bai, '%02d.in' % k), 'w').write(dau_vao)
        open(os.path.join(thu_muc_bai, '%02d.out' % k), 'w').write(dau_ra)

    with open(os.path.join(thu_muc_bai, 'init.yml'), 'w') as f:
        f.write('test_cases:\n')
        for k in range(1, n + 1):
            diem = chia + (1 if k <= du else 0)
            f.write('- in: %02d.in\n  out: %02d.out\n  points: %d\n'
                    % (k, k, diem))

    # Luu lai code de sau nay sinh them test duoc.
    open(os.path.join(thu_muc_bai, '_generator.py'), 'w').write(gen_code)
    open(os.path.join(thu_muc_bai, '_solver.py'), 'w').write(sol_code)

    return {
        'so_test': n,
        'so_lan_hong': so_lan_hong,
        'thu_muc': thu_muc_bai,
        'test_mau': cac_test[:3],
        'generator': gen_code,
        'solver': sol_code,
    }
