"""Sinh goi y AI cho nhieu bai, dung lai khi het han muc API."""

import time

from django.core.management.base import BaseCommand

from judge.models import Problem

from ai_assistant.llm_client import LoiGoiLLM
from ai_assistant.models import GoiY
from ai_assistant.services import LoiLuuBai, sinh_goi_y


class Command(BaseCommand):
    help = 'Sinh goi y AI cho nhung bai chua co'

    def add_arguments(self, parser):
        parser.add_argument('--so-bai', type=int, default=15,
                            help='Toi da bao nhieu bai trong mot lan chay')
        parser.add_argument('--nhom', type=str, default='',
                            help='Chi lam bai thuoc nhom nay (easy/medium/hard)')
        parser.add_argument('--nghi', type=int, default=3,
                            help='Nghi bao nhieu giay giua hai bai')

    def handle(self, *args, **opt):
        ds = Problem.objects.exclude(
            code__in=GoiY.objects.values_list('problem__code', flat=True)
        ).order_by('code')

        if opt['nhom']:
            ds = ds.filter(group__name=opt['nhom'])

        tong = ds.count()
        self.stdout.write('Con %d bai chua co goi y.' % tong)
        if not tong:
            return

        xong = 0
        hong = 0

        for bai in ds[:opt['so_bai']]:
            self.stdout.write('  %-12s ' % bai.code, ending='')
            self.stdout.flush()
            try:
                sinh_goi_y(bai)
                xong += 1
                self.stdout.write(self.style.SUCCESS('OK'))
            except (LoiGoiLLM, LoiLuuBai, ValueError) as e:
                hong += 1
                thong_bao = str(e)
                self.stdout.write(self.style.ERROR('HONG'))

                if '429' in thong_bao or 'RESOURCE_EXHAUSTED' in thong_bao:
                    self.stdout.write(self.style.WARNING(
                        'Het han muc API hom nay. Dung lai.'
                    ))
                    break
                self.stdout.write('    %s' % thong_bao[:200])

            time.sleep(opt['nghi'])

        self.stdout.write('')
        self.stdout.write('Xong %d bai, hong %d bai.' % (xong, hong))
        con_lai = tong - xong
        if con_lai > 0:
            self.stdout.write('Con %d bai chua lam. Chay lai lenh nay de tiep tuc.'
                              % con_lai)
