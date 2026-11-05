"""Chay code do AI sinh ra, co gioi han, trong thu muc tam.

Khong tin code AI: gioi han thoi gian, bo nho, va chay o thu muc rieng.
"""

import resource
import subprocess

GIOI_HAN_GIAY = 10
GIOI_HAN_RAM_MB = 512
GIOI_HAN_OUTPUT = 5 * 1024 * 1024   # 5 MB


class LoiChayCode(Exception):
    """Code chay hong: qua gio, loi cu phap, hoac in ra qua nhieu."""


def _dat_gioi_han():
    """Chay ngay truoc khi tien trinh con bat dau."""
    resource.setrlimit(resource.RLIMIT_AS,
                       (GIOI_HAN_RAM_MB * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE,
                       (GIOI_HAN_OUTPUT,) * 2)
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))


def chay_python(duong_dan, dau_vao='', thu_muc=None, giay=None,
                tham_so=None):
    """Chay mot file Python, tra ve stdout. Nem LoiChayCode neu hong."""
    try:
        kq = subprocess.run(
            ['python3', duong_dan] + list(tham_so or []),
            input=dau_vao,
            capture_output=True,
            text=True,
            timeout=giay or GIOI_HAN_GIAY,
            cwd=thu_muc,
            env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/tmp'},
            preexec_fn=_dat_gioi_han,
        )
    except subprocess.TimeoutExpired:
        raise LoiChayCode('Code chay qua %d giay, da dung.'
                          % (giay or GIOI_HAN_GIAY))
    except Exception as e:
        raise LoiChayCode('Khong chay duoc code: %r' % (e,))

    if kq.returncode != 0:
        raise LoiChayCode('Code loi (ma %d):\n%s'
                          % (kq.returncode, (kq.stderr or '')[:600]))

    if len(kq.stdout) > GIOI_HAN_OUTPUT:
        raise LoiChayCode('Code in ra qua nhieu du lieu.')

    return kq.stdout
