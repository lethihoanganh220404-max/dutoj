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
