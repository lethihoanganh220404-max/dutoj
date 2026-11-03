from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .llm_client import LoiGoiLLM, goi_llm
from .prompts import ANH_SANG_MARKDOWN
from .services import LoiLuuBai, luu_bai, tach_ten_bai

GIOI_HAN_MB = 8


@staff_member_required
def upload_image(request):
    ctx = {
        'title': 'AI hỗ trợ soạn đề',
        'time_limit': '1.0',
        'memory_limit': '262144',
        'points': '1',
    }

    if request.method != 'POST':
        return render(request, 'ai_assistant/upload.html', ctx)

    hanh_dong = request.POST.get('hanh_dong', 'doc_anh')

    # giu lai nhung gi nguoi dung da go
    for truong in ('ma_bai', 'ten_bai', 'time_limit', 'memory_limit', 'points'):
        if request.POST.get(truong):
            ctx[truong] = request.POST[truong]
    ctx['ket_qua'] = request.POST.get('ket_qua', '')

    if hanh_dong == 'doc_anh':
        anh = request.FILES.get('anh_de')
        if anh is None:
            ctx['loi'] = 'Chua chon file nao.'
        elif anh.size > GIOI_HAN_MB * 1024 * 1024:
            ctx['loi'] = 'Anh qua lon (toi da %d MB).' % GIOI_HAN_MB
        else:
            try:
                md = goi_llm(ANH_SANG_MARKDOWN,
                             anh_bytes=anh.read(),
                             mime_type=anh.content_type)
                ctx['ket_qua'] = md
                ctx.setdefault('ten_bai', tach_ten_bai(md))
            except LoiGoiLLM as e:
                ctx['loi'] = str(e)

    elif hanh_dong == 'luu_db':
        try:
            bai = luu_bai(
                ma=request.POST.get('ma_bai', ''),
                ten=request.POST.get('ten_bai', ''),
                mo_ta=request.POST.get('ket_qua', ''),
                time_limit=float(request.POST.get('time_limit') or 1.0),
                memory_limit=int(request.POST.get('memory_limit') or 262144),
                points=float(request.POST.get('points') or 1),
                nguoi_dung=request.user,
            )
            ctx['da_luu'] = bai.code
        except LoiLuuBai as e:
            ctx['loi'] = str(e)
        except (TypeError, ValueError):
            ctx['loi'] = 'Thoi gian / bo nho / diem phai la so.'

    return render(request, 'ai_assistant/upload.html', ctx)


@staff_member_required
def xem_goi_y(request, ma_bai):
    """Xem hoac sinh goi y 3 muc cho mot bai."""
    from django.shortcuts import get_object_or_404

    from judge.models import Problem

    from .models import GoiY
    from .services import sinh_goi_y

    bai = get_object_or_404(Problem, code=ma_bai)
    ctx = {'bai': bai, 'title': 'Gợi ý AI — %s' % bai.name}

    ctx['goi_y'] = GoiY.objects.filter(problem=bai).first()

    if request.method == 'POST':
        from .tasks import task_sinh_goi_y
        lam_lai = request.POST.get('lam_lai') == '1'
        ket = task_sinh_goi_y.delay(bai.id, lam_lai)
        ctx['task_id'] = ket.id
        ctx['dang_chay'] = True

    return render(request, 'ai_assistant/goi_y.html', ctx)


@staff_member_required
def trang_thai_task(request, task_id):
    """Trang web hoi lai moi vai giay: viec xong chua?"""
    from celery.result import AsyncResult
    from django.http import JsonResponse

    ket = AsyncResult(task_id)
    du_lieu = {'trang_thai': ket.state}

    if ket.successful():
        du_lieu['xong'] = True
    elif ket.failed():
        du_lieu['xong'] = True
        du_lieu['loi'] = str(ket.result)[:600]
    else:
        du_lieu['xong'] = False

    return JsonResponse(du_lieu)


@staff_member_required
def sinh_test(request, ma_bai):
    """Sinh test case bang AI cho mot bai."""
    import os

    from django.conf import settings
    from django.shortcuts import get_object_or_404

    from judge.models import Problem

    bai = get_object_or_404(Problem, code=ma_bai)

    goc = getattr(settings, 'DMOJ_PROBLEM_DATA_ROOT', '/problems')
    thu_muc = os.path.join(str(goc), bai.code)

    ctx = {'bai': bai, 'title': 'Sinh test case — %s' % bai.name}

    # Dem xem da co bao nhieu test
    if os.path.isdir(thu_muc):
        ctx['so_test_hien_co'] = len(
            [t for t in os.listdir(thu_muc)
             if t.endswith('.in') and not t.startswith('_')]
        )
        ctx['co_init'] = os.path.isfile(os.path.join(thu_muc, 'init.yml'))

    from .models import TestCaseNhap
    nhap = TestCaseNhap.objects.filter(problem=bai).first()
    ctx['nhap'] = nhap

    if nhap:
        import json
        ctx['canh_bao_da_dap_an'] = 'YES' in (nhap.da_dap_an or '').upper()
        cac_test = json.loads(nhap.du_lieu or '[]')
        ctx['test_mau'] = [
            {'stt': i + 1, 'vao': v[:500], 'ra': r[:300]}
            for i, (v, r) in enumerate(cac_test[:3])
        ]

    if request.method == 'POST':
        hanh_dong = request.POST.get('hanh_dong', 'sinh')

        if hanh_dong == 'duyet' and nhap:
            from .services import ghi_test_case
            try:
                kq = ghi_test_case(nhap)
                ctx['da_ghi'] = kq
            except LoiLuuBai as e:
                ctx['loi'] = str(e)

        elif hanh_dong == 'sinh_checker' and nhap:
            from .tasks import task_sinh_checker
            ket = task_sinh_checker.delay(nhap.id)
            ctx['task_id'] = ket.id
            ctx['dang_chay_checker'] = True

        elif hanh_dong == 'bo' and nhap:
            nhap.delete()
            ctx['nhap'] = None
            ctx['test_mau'] = None
            ctx['da_bo'] = True

        else:
            from .tasks import task_sinh_test_case
            try:
                so_test = int(request.POST.get('so_test') or 15)
            except ValueError:
                so_test = 15
            so_test = max(5, min(so_test, 30))
            ket = task_sinh_test_case.delay(bai.id, so_test)
            ctx['task_id'] = ket.id
            ctx['dang_chay'] = True
            ctx['so_test_yeu_cau'] = so_test

    return render(request, 'ai_assistant/sinh_test.html', ctx)
