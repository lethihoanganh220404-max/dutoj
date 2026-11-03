from django.db import models

from judge.models import Problem


class GoiY(models.Model):
    """Goi y 3 muc do AI sinh ra cho mot bai. Luu lai de khong goi API lai."""

    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name='ai_goi_y',
        verbose_name='bai tap',
    )
    muc1 = models.TextField('muc 1 - huong tiep can', blank=True)
    muc2 = models.TextField('muc 2 - thuat toan', blank=True)
    muc3 = models.TextField('muc 3 - loi giai chi tiet', blank=True)

    mo_hinh = models.CharField('mo hinh da dung', max_length=100, blank=True)
    ngay_tao = models.DateTimeField('ngay tao', auto_now_add=True)
    ngay_sua = models.DateTimeField('ngay sua', auto_now=True)

    class Meta:
        verbose_name = 'goi y AI'
        verbose_name_plural = 'goi y AI'

    def __str__(self):
        return 'Goi y cho %s' % self.problem.code
