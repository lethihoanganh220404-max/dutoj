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
