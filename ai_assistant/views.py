from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .llm_client import LoiGoiLLM, goi_llm
from .prompts import ANH_SANG_MARKDOWN
from .services import LoiLuuBai, luu_bai, tach_ten_bai

GIOI_HAN_MB = 8


@staff_member_required
def upload_image(request):
    ctx = {
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
    ctx = {'bai': bai}

    if request.method == 'POST':
        lam_lai = request.POST.get('lam_lai') == '1'
        try:
            goi_y, da_goi_api = sinh_goi_y(bai, bat_buoc_goi_lai=lam_lai)
            ctx['goi_y'] = goi_y
            ctx['da_goi_api'] = da_goi_api
        except (LoiGoiLLM, LoiLuuBai, ValueError) as e:
            ctx['loi'] = str(e)
            ctx['goi_y'] = GoiY.objects.filter(problem=bai).first()
    else:
        ctx['goi_y'] = GoiY.objects.filter(problem=bai).first()

    return render(request, 'ai_assistant/goi_y.html', ctx)
