from django.db import models

# Create your models here.
class Site(models.Model):
    """场站/站点模型"""
    SITE_TYPE_CHOICES = [
        ('wind', '风电'),
        ('sun', '光伏')
    ]
    
    # 基础信息
    name = models.CharField(max_length=100, unique=True, verbose_name="场站名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="场站代码")

    
    # 联系信息
    address = models.CharField(max_length=200, verbose_name="详细地址")
    phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    email = models.EmailField(blank=True, verbose_name="联系邮箱")
    manager_name = models.CharField(max_length=50, blank=True, verbose_name="负责人姓名")
    
    # 业务信息
    description = models.TextField(blank=True, verbose_name="场站描述")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "场站"
        verbose_name_plural = "场站管理"
        ordering = ['code']  # 按代码排序
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
