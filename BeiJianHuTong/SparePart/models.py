from django.db import models
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    """备件分类模型"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="分类描述")
    code = models.CharField(max_length=20, unique=True, verbose_name="分类编码")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "备件分类"
        verbose_name_plural = "备件分类"
        ordering = ['code']
    
    def __str__(self):
        return self.name


class SparePart(models.Model):
    """备件模型"""
    
    id = models.AutoField(primary_key=True, verbose_name="ID")

    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '停用'),
        ('obsolete', '已淘汰'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name="备件名称")
    model = models.CharField(
        max_length=200,
        default='UNKNOWN',  # ✅ 添加默认值
        verbose_name="备件型号"
    ) #改为小写
    description = models.TextField(blank=True, verbose_name="备件描述")  # 新增
    
    # ✅ 改为外键关联 Category
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='spare_parts',
        verbose_name="备件分类",
         null=True,  # ✅ 允许为空
        blank=True,  # ✅ 前端表单可选
        default=None  # ✅ 默认为空（需要手动选择或创建）
    )
    
    
    quantity = models.PositiveIntegerField(default=0, verbose_name="当前数量")
    alarm_qty = models.PositiveIntegerField(default=5, verbose_name="库存预警数量")  # 新增
    location = models.CharField(max_length=200, blank=True, default='', verbose_name="备件位置")
    image = models.ImageField(upload_to='spare_parts/', blank=True, null=True, verbose_name="备件图片")
    
    # 供应商信息
    supplier = models.CharField(max_length=100, blank=True, verbose_name="供应商名称")  # 新增
    supplier_code = models.CharField(max_length=100, blank=True, verbose_name="供应商编码")  # 新增
    procurement_days = models.PositiveIntegerField(default=7, verbose_name="采购周期（天）")  # 新增
    
    # 关联场站
    site = models.ForeignKey(
        'sites.Site', 
        on_delete=models.CASCADE,
        related_name='spare_parts',
        verbose_name="所属场站"
    )
    
    # 状态和操作人
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="状态"
    )  # 新增
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_spare_parts',
        verbose_name="创建人"
    )  # 新增
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_spare_parts',
        verbose_name="更新人"
    )  # 新增
    
    # 最后操作时间
    last_purchase_date = models.DateTimeField(null=True, blank=True, verbose_name="最后采购日期")  # 新增
    last_use_date = models.DateTimeField(null=True, blank=True, verbose_name="最后使用日期")  # 新增
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "备件"
        verbose_name_plural = "备件管理"
        ordering = ['site', 'name']
        unique_together = ['name', 'site']
    
    def __str__(self):
        return f"{self.name} ({self.quantity}个) - {self.site.name}"


class SparePartTransaction(models.Model):
    """备件出入库记录模型"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('in', '入库'),
        ('out', '出库'),
    ]
    
    spare_part = models.ForeignKey(
        SparePart,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="备件"
    )
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name="操作类型"
    )
    
    quantity = models.PositiveIntegerField(verbose_name="数量")
    
    # 操作人员
    operator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='spare_part_transactions',
        verbose_name="操作人"
    )
    
    # 操作详情
    reason = models.CharField(max_length=200, verbose_name="操作原因")
    remark = models.TextField(blank=True, verbose_name="备注")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    
    class Meta:
        verbose_name = "备件出入库记录"
        verbose_name_plural = "备件出入库记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.spare_part.name} {self.get_transaction_type_display()} {self.quantity}个"
    
    def save(self, *args, **kwargs):
        """保存时更新备件库存数量和最后使用日期"""
        if not self.pk:  # 只在创建时执行
            if self.transaction_type == 'in':
                self.spare_part.quantity += self.quantity
                self.spare_part.last_purchase_date = timezone.now()  # 更新最后采购日期
            elif self.transaction_type == 'out':
                self.spare_part.quantity -= self.quantity
                self.spare_part.last_use_date = timezone.now()  # 更新最后使用日期
            
            self.spare_part.save(update_fields=['quantity', 'last_purchase_date', 'last_use_date'])
        
        super().save(*args, **kwargs)

# 插入样本备件数据
# 假设 site_id = 1（北京场站），user_id = 5（admin用户）

