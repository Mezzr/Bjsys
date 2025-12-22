from django.contrib import admin
from .models import Category, SparePart, SparePartTransaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """分类管理"""
    list_display = ['id', 'name', 'code', 'is_active', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    """备件管理"""
    list_display = ['id', 'name', 'model', 'category', 'quantity', 'alarm_qty', 'site', 'status', 'created_at']
    search_fields = ['name', 'model', 'supplier']
    list_filter = ['status', 'category', 'site', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'model', 'description', 'category')
        }),
        ('库存信息', {
            'fields': ('quantity', 'alarm_qty', 'location', 'image')
        }),
        ('供应商信息', {
            'fields': ('supplier', 'supplier_code', 'procurement_days')
        }),
        ('场站与状态', {
            'fields': ('site', 'status')
        }),
        ('操作记录', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('使用记录', {
            'fields': ('last_purchase_date', 'last_use_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """自动设置创建人和更新人"""
        if not change:  # 创建时
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SparePartTransaction)
class SparePartTransactionAdmin(admin.ModelAdmin):
    """出入库记录管理"""
    list_display = ['id', 'spare_part', 'transaction_type', 'quantity', 'operator', 'created_at']
    search_fields = ['spare_part__name', 'reason']
    list_filter = ['transaction_type', 'created_at']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        """自动设置操作人"""
        if not change:  # 创建时
            obj.operator = request.user
        super().save_model(request, obj, form, change)