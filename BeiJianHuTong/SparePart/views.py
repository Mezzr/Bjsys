from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import SparePart, Category, SparePartTransaction
from .serializers import SparePartSerializer, CategorySerializer, SparePartTransactionSerializer


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    page_size_query_description = "每页数量"


class CategoryViewSet(viewsets.ModelViewSet):
    """分类管理接口"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """获取所有分类（自定义响应格式）"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 0,
            "message": "success",
            "data": serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个分类"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 0,
            "message": "success",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建分类"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 0,
            "message": "创建成功",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class SparePartTransactionViewSet(viewsets.ModelViewSet):
    """出入库记录管理"""
    queryset = SparePartTransaction.objects.all()
    serializer_class = SparePartTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def list(self, request, *args, **kwargs):
        """获取出入库记录列表"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 按备件筛选
        spare_part_id = request.query_params.get('spare_part_id')
        if spare_part_id:
            queryset = queryset.filter(spare_part_id=spare_part_id)
        
        # 按操作类型筛选
        transaction_type = request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # 按时间范围筛选
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                "code": 0,
                "message": "success",
                "data": {
                    "total": paginated_response.data['count'],
                    "page": int(request.query_params.get('page', 1)),
                    "limit": self.pagination_class.page_size,
                    "items": serializer.data
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 0,
            "message": "success",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建出入库记录（自动创建备件）"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # 自动设置操作人
        transaction = serializer.save(operator=request.user)
        
        return Response({
            "code": 0,
            "message": "创建成功",
            "data": SparePartTransactionSerializer(transaction, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_spare_part(self, request):
        """获取指定备件的所有出入库记录"""
        spare_part_id = request.query_params.get('spare_part_id')
        if not spare_part_id:
            return Response({
                "code": 1,
                "message": "spare_part_id 参数缺失",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        spare_part = get_object_or_404(SparePart, id=spare_part_id)
        transactions = spare_part.transactions.all()
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                "code": 0,
                "message": "success",
                "data": {
                    "spare_part": {
                        "id": spare_part.id,
                        "name": spare_part.name,
                        "current_quantity": spare_part.quantity
                    },
                    "total": paginated_response.data['count'],
                    "page": int(request.query_params.get('page', 1)),
                    "limit": self.pagination_class.page_size,
                    "items": serializer.data
                }
            })
        
        serializer = self.get_serializer(transactions, many=True)
        return Response({
            "code": 0,
            "message": "success",
            "data": {
                "spare_part": {
                    "id": spare_part.id,
                    "name": spare_part.name,
                    "current_quantity": spare_part.quantity
                },
                "items": serializer.data
            }
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取出入库统计数据"""
        spare_part_id = request.query_params.get('spare_part_id')
        
        if spare_part_id:
            transactions = SparePartTransaction.objects.filter(spare_part_id=spare_part_id)
        else:
            transactions = SparePartTransaction.objects.all()
        
        # 统计入库和出库
        in_count = transactions.filter(transaction_type='in').count()
        out_count = transactions.filter(transaction_type='out').count()
        
        in_qty = sum([t.quantity for t in transactions.filter(transaction_type='in')])
        out_qty = sum([t.quantity for t in transactions.filter(transaction_type='out')])
        
        return Response({
            "code": 0,
            "message": "success",
            "data": {
                "total_transactions": transactions.count(),
                "in": {
                    "count": in_count,
                    "quantity": in_qty
                },
                "out": {
                    "count": out_count,
                    "quantity": out_qty
                }
            }
        })


class SparePartViewSet(viewsets.ModelViewSet):
    """备件管理接口"""
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def list(self, request, *args, **kwargs):
        """获取备件列表（分页）"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 支持按分类筛选
        category_id = request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 支持按场站筛选
        site_id = request.query_params.get('site_id')
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        
        # 权限控制：如果用户不能查看所有场站，则强制只能查看自己场站的备件
        if not request.user.can_view_all_sites and request.user.site:
            queryset = queryset.filter(site=request.user.site)

        # 支持按状态筛选
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 支持搜索
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(model__icontains=search)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                "code": 0,
                "message": "success",
                "data": {
                    "total": paginated_response.data['count'],
                    "page": int(request.query_params.get('page', 1)),
                    "limit": self.pagination_class.page_size,
                    "items": serializer.data
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 0,
            "message": "success",
            "data": serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个备件"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 0,
            "message": "success",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建备件"""
        # 优先使用请求中的 siteId，否则使用用户关联的 site
        site_id = request.data.get('siteId')
        site = None
        
        if site_id:
            from sites.models import Site
            site = get_object_or_404(Site, id=site_id)
        elif request.user.site:
            site = request.user.site
            
        if not site:
             return Response({
                "code": 1,
                "message": "未指定场站，且当前用户未关联场站",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 自动设置创建人 和 场站
        spare_part = serializer.save(
            created_by=request.user, 
            updated_by=request.user,
            site=site
        )
        
        return Response({
            "code": 0,
            "message": "创建成功",
            "data": SparePartSerializer(spare_part).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """更新备件"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 自动设置更新人
        spare_part = serializer.save(updated_by=request.user)
        
        return Response({
            "code": 0,
            "message": "更新成功",
            "data": SparePartSerializer(spare_part).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除备件"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 0,
            "message": "删除成功"
        }, status=status.HTTP_204_NO_CONTENT)
