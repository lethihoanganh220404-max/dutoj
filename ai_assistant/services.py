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
