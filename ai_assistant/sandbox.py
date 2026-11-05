"""Chay code do AI sinh ra trong container cach ly.

Khong tin code AI. Moi lan chay deu dung mot container rieng, dung chung
anh judge - cung moi truong ma he thong dung de cham bai nguoi dung nop.
Container bi chan mang, chi doc he thong file, gioi han RAM va CPU.
"""

import os
import shutil
import tempfile

import docker
from docker.errors import ContainerError, DockerException, ImageNotFound

ANH_CHAY = os.environ.get('AI_ANH_CHAY', 'dutoj-judge:latest')
THU_MUC_CHUNG = os.environ.get('AI_THU_MUC_CHUNG', '/ai_work')
# Ten volume nhu Docker tren may host nhin thay (khac duong dan trong container)
TEN_VOLUME = os.environ.get('AI_TEN_VOLUME', 'dutoj_ai_work')

GIOI_HAN_GIAY = 10
GIOI_HAN_RAM_MB = 512
GIOI_HAN_OUTPUT = 5 * 1024 * 1024   # 5 MB


class LoiChayCode(Exception):
    """Code chay hong: qua gio, loi cu phap, hoac in ra qua nhieu."""


def _lay_client():
    try:
        return docker.from_env()
    except DockerException as e:
        raise LoiChayCode('Khong noi duoc voi Docker: %r' % (e,))


def chay_python(duong_dan, dau_vao='', thu_muc=None, giay=None,
                tham_so=None):
    """Chay mot file Python trong container, tra ve stdout.

    Giu nguyen chu ky ham cu nen cho goi khong phai sua.
    """
    giay = giay or GIOI_HAN_GIAY
    thu_muc = thu_muc or os.path.dirname(duong_dan)

    # Chep ca thu muc lam viec sang volume dung chung, de container thay duoc.
    os.makedirs(THU_MUC_CHUNG, exist_ok=True)
    # Volume moi tao chi root ghi duoc; container chay bang user 1000.
    try:
        os.chmod(THU_MUC_CHUNG, 0o777)
    except OSError:
        pass
    hop = tempfile.mkdtemp(dir=THU_MUC_CHUNG)
    try:
        for ten in os.listdir(thu_muc):
            nguon = os.path.join(thu_muc, ten)
            if os.path.isfile(nguon):
                shutil.copy2(nguon, os.path.join(hop, ten))

        # Container chay bang user 1000, khong phai root -> phai mo quyen doc.
        os.chmod(hop, 0o755)
        for ten in os.listdir(hop):
            os.chmod(os.path.join(hop, ten), 0o644)

        ten_file = os.path.basename(duong_dan)
        lenh = ['python3', ten_file] + [str(x) for x in (tham_so or [])]

        cli = _lay_client()
        try:
            thung = cli.containers.create(
                ANH_CHAY,
                entrypoint='',
                command=lenh,
                working_dir='/ai_work/' + os.path.basename(hop),
                volumes={TEN_VOLUME: {'bind': '/ai_work', 'mode': 'rw'}},
                network_mode='none',          # chan mang
                read_only=True,               # chan ghi he thong file
                tmpfs={'/tmp': 'size=64m'},   # tru /tmp nho
                mem_limit='%dm' % GIOI_HAN_RAM_MB,
                memswap_limit='%dm' % GIOI_HAN_RAM_MB,   # chan tran sang swap
                pids_limit=64,
                nano_cpus=1_000_000_000,      # toi da 1 CPU
                environment={'HOME': '/tmp', 'PYTHONDONTWRITEBYTECODE': '1'},
                stdin_open=bool(dau_vao),
                user='1000:1000',
            )
        except ImageNotFound:
            raise LoiChayCode('Khong tim thay anh %s.' % ANH_CHAY)

        try:
            if dau_vao:
                ong = thung.attach_socket(
                    params={'stdin': 1, 'stream': 1})
                thung.start()
                ong._sock.sendall(dau_vao.encode())
                ong._sock.shutdown(1)      # bao da het dau vao
                ong.close()
            else:
                thung.start()

            try:
                ket = thung.wait(timeout=giay)
            except Exception:
                thung.kill()
                raise LoiChayCode('Code chay qua %d giay, da dung.' % giay)

            ra = thung.logs(stdout=True, stderr=False)
            loi = thung.logs(stdout=False, stderr=True)

            if len(ra) > GIOI_HAN_OUTPUT:
                raise LoiChayCode('Code in ra qua nhieu du lieu.')

            ma = ket.get('StatusCode', -1)
            if ma != 0:
                raise LoiChayCode('Code loi (ma %d):\n%s'
                                  % (ma, loi.decode('utf-8', 'replace')[:600]))

            return ra.decode('utf-8', 'replace')
        finally:
            try:
                thung.remove(force=True)
            except Exception:
                pass

    except ContainerError as e:
        raise LoiChayCode('Code loi: %s' % str(e)[:600])
    finally:
        shutil.rmtree(hop, ignore_errors=True)
