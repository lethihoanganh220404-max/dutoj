"""Lop truu tuong goi LLM. Doi nha cung cap chi bang doi bien moi truong."""

import base64
import json
import os
import time
import urllib.error
import urllib.request

API_KEY = os.environ.get('GEMINI_API_KEY', '')
OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OR_MODEL = os.environ.get('OPENROUTER_MODEL', '')
MODEL = os.environ.get('AI_MODEL', 'gemini-3.8-flash')
TIMEOUT = int(os.environ.get('AI_TIMEOUT', '240'))

ENDPOINT = (
    'https://generativelanguage.googleapis.com/v1beta/models/'
    '{model}:generateContent'
)


class LoiGoiLLM(Exception):
    """Loi khi goi API. Bat rieng de hien thong bao de hieu cho nguoi dung."""


def _goi_gemini(prompt, anh_bytes=None, mime_type=None):
    if not API_KEY:
        raise LoiGoiLLM(
            'Chua co GEMINI_API_KEY. Them vao file .env roi khoi dong lai container.'
        )

    parts = []
    if anh_bytes:
        parts.append({
            'inline_data': {
                'mime_type': mime_type or 'image/jpeg',
                'data': base64.b64encode(anh_bytes).decode('ascii'),
            }
        })
    parts.append({'text': prompt})

    payload = {'contents': [{'parts': parts}]}

    req = urllib.request.Request(
        ENDPOINT.format(model=MODEL),
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': API_KEY,
        },
        method='POST',
    )

    # Loi 429 (het han muc tam thoi) va 503 (may chu qua tai) la loi tam thoi:
    # cho roi thu lai. Cac loi khac bao ngay vi thu lai cung vo ich.
    LOI_TAM_THOI = (429, 503)
    SO_LAN_THU = int(os.environ.get('AI_SO_LAN_THU', '4'))
    data = None

    for lan in range(SO_LAN_THU):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            break
        except urllib.error.HTTPError as e:
            chi_tiet = e.read().decode('utf-8', 'replace')[:600]
            if e.code in LOI_TAM_THOI and lan < SO_LAN_THU - 1:
                time.sleep(2 ** lan * 3)   # cho 3, 6, 12 giay
                continue
            raise LoiGoiLLM(
                'API tra ve loi %s (da thu %d lan):\n%s'
                % (e.code, lan + 1, chi_tiet)
            )
        except Exception as e:
            # Het gio cho hoac mang chap chon: cung la loi tam thoi, thu lai.
            if lan < SO_LAN_THU - 1:
                time.sleep(2 ** lan * 3)
                continue
            raise LoiGoiLLM(
                'Khong goi duoc API sau %d lan thu: %r' % (SO_LAN_THU, e)
            )

    try:
        cac_phan = data['candidates'][0]['content']['parts']
    except (KeyError, IndexError):
        raise LoiGoiLLM('API tra ve du lieu la:\n' + json.dumps(data)[:600])

    van_ban = [p['text'] for p in cac_phan
               if 'text' in p and not p.get('thought')]
    if not van_ban:
        raise LoiGoiLLM('API khong tra ve van ban nao.')

    return '\n'.join(van_ban).strip()


OR_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'


def _goi_openrouter(prompt, anh_bytes=None, mime_type=None):
    """Nha cung cap du phong. Dung giao dien kieu OpenAI."""
    if not OR_KEY:
        raise LoiGoiLLM('Chua co OPENROUTER_API_KEY trong .env')

    noi_dung = []
    if anh_bytes:
        b64 = base64.b64encode(anh_bytes).decode('ascii')
        noi_dung.append({
            'type': 'image_url',
            'image_url': {
                'url': 'data:%s;base64,%s' % (mime_type or 'image/jpeg', b64),
            },
        })
    noi_dung.append({'type': 'text', 'text': prompt})

    payload = {
        'model': OR_MODEL,
        'messages': [{'role': 'user', 'content': noi_dung}],
    }

    req = urllib.request.Request(
        OR_ENDPOINT,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + OR_KEY,
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        chi_tiet = e.read().decode('utf-8', 'replace')[:600]
        raise LoiGoiLLM('OpenRouter tra ve loi %s:\n%s' % (e.code, chi_tiet))
    except Exception as e:
        raise LoiGoiLLM('Khong goi duoc OpenRouter: %r' % (e,))

    try:
        return data['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, AttributeError):
        raise LoiGoiLLM('OpenRouter tra ve du lieu la:\n'
                        + json.dumps(data)[:600])


def goi_llm(prompt, anh_bytes=None, mime_type=None):
    """Thu Gemini truoc. Gemini nghen thi tu chuyen sang OpenRouter."""
    try:
        return _goi_gemini(prompt, anh_bytes, mime_type)
    except LoiGoiLLM as loi_gemini:
        if not OR_KEY:
            raise
        try:
            return _goi_openrouter(prompt, anh_bytes, mime_type)
        except LoiGoiLLM as loi_or:
            raise LoiGoiLLM(
                'Ca hai nha cung cap deu hong.\n\n'
                '--- Gemini ---\n%s\n\n'
                '--- OpenRouter ---\n%s' % (loi_gemini, loi_or)
            )
