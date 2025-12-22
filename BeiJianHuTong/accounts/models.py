from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
# Create your models here.
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class User(AbstractUser):
    """自定义用户模型，扩展了场站关联"""
    
    
    
    # 关联场站 - 关键字段
    site = models.ForeignKey(
        'sites.Site', 
        on_delete=models.PROTECT,  # 保护模式，防止误删场站导致用户无归属
        related_name='users',
        verbose_name="所属场站",
        null=True,  # 超级管理员可能不需要关联特定场站
        blank=True
    )
    
   
    
    # 权限标记
    can_edit_own_site = models.BooleanField(default=True, verbose_name="可编辑本场站备件")
    can_view_all_sites = models.BooleanField(default=False, verbose_name="可查看所有场站备件")
    can_manage_users = models.BooleanField(default=False, verbose_name="可管理用户")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"
        ordering = ['site', 'username']
    
    def __str__(self):
        if self.site:
            return f"{self.username} - {self.site.name}"
        return f"{self.username} (未分配场站)"
    
    # def clean(self):
    #     """数据验证"""
    #     # 特定角色的用户必须有场站
    #     # roles_requiring_site = ['site_admin']
    #     # if self.role in roles_requiring_site and not self.site:
    #     #     raise ValidationError(f"{self.get_role_display()}必须关联一个场站")
        
    #     # 超级管理员可以不关联场站，但关联后只能管理该场站
    #     if self.role == 'superadmin' and self.site:
    #         self.can_view_all_sites = True
    
#     def save(self, *args, **kwargs):
#         """保存时自动设置权限"""
#         self.full_clean()  # 调用验证
# #        self.set_permissions_by_role()
#         super().save(*args, **kwargs)
    
    # def set_permissions_by_role(self):
    #     """根据角色自动设置权限标记"""
    #     role_permissions = {
    #         'superadmin': {
    #             'can_edit_own_site': True,
    #             'can_view_all_sites': True,
    #             'can_manage_users': True,
    #             'is_staff': True,
    #             'is_superuser': True,
    #         },
    #         'site_admin': {
    #             'can_edit_own_site': True,
    #             'can_view_all_sites': True,
    #             'can_manage_users': True,
    #             'is_staff': True,
    #             'is_superuser': False,
    #         }
    #     }
        
    #     if self.role in role_permissions:
    #         for perm, value in role_permissions[self.role].items():
    #             setattr(self, perm, value)
    
    def get_site_name(self):
        """获取场站名称（安全方法）"""
        return self.site.name if self.site else "未分配"
    
    def can_edit_spare_part(self, spare_part):
        """检查用户是否有权限编辑特定备件"""
        if not self.can_edit_own_site:
            return False
        # 用户只能编辑自己场站的备件，除非有特殊权限
        if self.can_view_all_sites:
            return True
        return self.site == spare_part.site
    
