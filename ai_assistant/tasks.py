"""Cac viec chay nen. Goi LLM mat 10-60 giay, chay dong bo thi web treo."""

from celery import shared_task


@shared_task(bind=True)
def task_sinh_goi_y(self, problem_id, lam_lai=False):
    from judge.models import Problem

    from .services import sinh_goi_y

    bai = Problem.objects.get(id=problem_id)
    goi_y, da_goi_api = sinh_goi_y(bai, bat_buoc_goi_lai=lam_lai)
    return {
        'problem_id': problem_id,
        'da_goi_api': da_goi_api,
        'ok': True,
    }


@shared_task(bind=True)
def task_sinh_test_case(self, problem_id, so_test=15):
    from judge.models import Problem

    from .services import sinh_test_case

    bai = Problem.objects.get(id=problem_id)
    kq = sinh_test_case(bai, so_test=so_test)
    # Bo phan code dai, chi giu so lieu de hien len web.
    return {
        'so_test': kq['so_test'],
        'so_lan_hong': kq['so_lan_hong'],
        'thu_muc': kq['thu_muc'],
        'ok': True,
    }


@shared_task(bind=True)
def task_sinh_checker(self, nhap_id):
    from .models import TestCaseNhap
    from .services import sinh_checker

    nhap = TestCaseNhap.objects.get(id=nhap_id)
    sinh_checker(nhap)
    return {'ok': True, 'nhap_id': nhap_id}
