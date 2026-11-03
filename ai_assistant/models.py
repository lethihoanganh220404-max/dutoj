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


class TestCaseNhap(models.Model):
    """Test case AI vua sinh, cho nguoi duyet truoc khi ghi ra /problems."""

    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name='ai_test_nhap',
        verbose_name='bai tap',
    )
    generator = models.TextField('code sinh du lieu vao', blank=True)
    solver = models.TextField('code giai tham chieu', blank=True)
    du_lieu = models.TextField('cac cap input/output dang JSON', blank=True)

    so_test = models.PositiveIntegerField('so test', default=0)
    so_lan_hong = models.PositiveIntegerField('so lan chay hong', default=0)
    da_duyet = models.BooleanField('da duyet va ghi ra /problems', default=False)

    da_dap_an = models.TextField('AI bao bai co nhieu dap an dung khong',
                                blank=True)
    ngay_tao = models.DateTimeField('ngay tao', auto_now_add=True)

    class Meta:
        verbose_name = 'test case nhap'
        verbose_name_plural = 'test case nhap'

    def __str__(self):
        return 'Test nhap cho %s (%d test)' % (self.problem.code, self.so_test)
