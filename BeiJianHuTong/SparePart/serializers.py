from rest_framework import serializers
from .models import SparePart, Category, SparePartTransaction

class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'code', 'is_active', 'created_at', 'updated_at']


class SparePartTransactionSerializer(serializers.ModelSerializer):
    """出入库记录序列化器"""
    
    operator_name = serializers.CharField(source='operator.username', read_only=True, allow_null=True)
    spare_part_name = serializers.CharField(source='spare_part.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    # ✅ 新增：自动创建备件的字段
    spare_part_name_input = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="备件名称（如果备件不存在则自动创建）")
    spare_part_model = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="备件型号")
    spare_part_location = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="备件位置")
    spare_part_category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, help_text="备件分类ID")
    spare_part_site_id = serializers.IntegerField(write_only=True, required=False, help_text="场站ID")
    
    class Meta:
        model = SparePartTransaction
        fields = [
            'id', 'spare_part', 'spare_part_name', 'transaction_type', 
            'transaction_type_display', 'quantity', 'operator', 'operator_name',
            'reason', 'remark', 'created_at',
            # ✅ 新增字段
            'spare_part_name_input', 'spare_part_model', 'spare_part_location',
            'spare_part_category_id', 'spare_part_site_id'
        ]
        read_only_fields = ['id', 'created_at', 'spare_part_name', 'transaction_type_display']
    
    def create(self, validated_data):
        """创建出入库记录，如果备件不存在则自动创建"""
        
        # ✅ 提取自动创建备件的字段
        spare_part_name_input = validated_data.pop('spare_part_name_input', None)
        spare_part_model = validated_data.pop('spare_part_model', 'UNKNOWN')
        spare_part_location = validated_data.pop('spare_part_location', '未指定')
        spare_part_category_id = validated_data.pop('spare_part_category_id', None)
        spare_part_site_id = validated_data.pop('spare_part_site_id', None)
        
        # 检查 spare_part 是否已提供
        spare_part = validated_data.get('spare_part')
        
        # 如果没有提供 spare_part ID，但提供了备件名称，则尝试自动创建或查找
        if not spare_part and spare_part_name_input:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            from sites.models import Site
            
            # 获取场站
            if not spare_part_site_id:
                raise serializers.ValidationError("必须提供 spare_part 或 spare_part_site_id")
            
            try:
                site = Site.objects.get(id=spare_part_site_id)
            except Site.DoesNotExist:
                raise serializers.ValidationError(f"场站 ID {spare_part_site_id} 不存在")
            
            # 获取分类（如果提供）
            category = None
            if spare_part_category_id:
                try:
                    category = Category.objects.get(id=spare_part_category_id)
                except Category.DoesNotExist:
                    raise serializers.ValidationError(f"分类 ID {spare_part_category_id} 不存在")
            
            # ✅ 自动创建备件
            spare_part, created = SparePart.objects.get_or_create(
                name=spare_part_name_input,
                site=site,
                defaults={
                    'model': spare_part_model,
                    'location': spare_part_location,
                    'category': category,
                    'quantity': 0,
                    'alarm_qty': 5,
                    'status': 'active',
                    'created_by': self.context['request'].user if 'request' in self.context else None,
                    'updated_by': self.context['request'].user if 'request' in self.context else None,
                }
            )
            
            # 更新 validated_data 中的 spare_part
            validated_data['spare_part'] = spare_part
        
        elif not spare_part:
            raise serializers.ValidationError("必须提供 spare_part 或 spare_part_name_input")
        
        # 创建出入库记录
        transaction = SparePartTransaction.objects.create(**validated_data)
        return transaction


class SparePartSerializer(serializers.ModelSerializer):
    stationId = serializers.CharField(source='site.id', read_only=True)
    stationName = serializers.CharField(source='site.name', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True, allow_null=True)
    imageUrl = serializers.SerializerMethodField()
    alarmQty = serializers.IntegerField(source='alarm_qty')
    procurementDays = serializers.IntegerField(source='procurement_days')
    category = CategorySerializer(read_only=True, allow_null=True)
    # ✅ 修改：使用 PrimaryKeyRelatedField 正确处理写入
    categoryId = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True, 
        allow_null=True, 
        required=False
    )
    siteId = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    categoryName = serializers.SerializerMethodField()
    
    class Meta:
        model = SparePart
        fields = [
            'id', 'name', 'model', 'description', 'location',
            'supplier', 'supplier_code', 'quantity', 'alarmQty',
            'procurementDays', 'imageUrl', 'stationId', 'stationName', 'siteId', 'category',
            'categoryId', 'categoryName', 'status', 'created_by', 'created_at', 'updated_by',
            'updated_at', 'last_purchase_date', 'last_use_date'
        ]
    
    def create(self, validated_data):
        validated_data.pop('siteId', None)
        return super().create(validated_data)

    def get_imageUrl(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_categoryName(self, obj):
        return obj.category.name if obj.category else "未分类"