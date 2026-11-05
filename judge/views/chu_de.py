"""Trang liet ke cac chu de bai tap."""

from django.db.models import Count, Q
from django.shortcuts import render
from django.utils.translation import gettext as _

from judge.models import ProblemType


def danh_sach_chu_de(request):
    """Hien 17 chu de dang the, kem so bai cua moi chu de."""
    ds = (ProblemType.objects
          .annotate(so_bai=Count('problem',
                                 filter=Q(problem__is_public=True)))
          .filter(so_bai__gt=0)
          .order_by('-so_bai'))

    return render(request, 'problem/chu-de.html', {
        'title': _('Chủ đề'),
        'danh_sach': ds,
        'nav_tab': 'chu_de',
    })
