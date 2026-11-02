from django.shortcuts import render

from .llm_client import LoiGoiLLM, goi_llm
from .prompts import ANH_SANG_MARKDOWN

GIOI_HAN_MB = 8


def upload_image(request):
    ket_qua = None
    loi = None

    if request.method == 'POST':
        anh = request.FILES.get('anh_de')

        if anh is None:
            loi = 'Chua chon file nao.'
        elif anh.size > GIOI_HAN_MB * 1024 * 1024:
            loi = 'Anh qua lon (toi da %d MB).' % GIOI_HAN_MB
        else:
            try:
                ket_qua = goi_llm(
                    ANH_SANG_MARKDOWN,
                    anh_bytes=anh.read(),
                    mime_type=anh.content_type,
                )
            except LoiGoiLLM as e:
                loi = str(e)

    return render(request, 'ai_assistant/upload.html',
                  {'ket_qua': ket_qua, 'loi': loi})
