from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User, Warehouse, Video, Report
from .serializers import UserSerializer, WarehouseSerializer, VideoSerializer, ReportSerializer


class IsSysAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.ROLE_SYSADMIN)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.ROLE_ADMIN)


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.ROLE_WORKER)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            role = self.request.data.get('role')
            if role == User.ROLE_ADMIN:
                return [IsSysAdmin()]
            if role == User.ROLE_WORKER:
                return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        role = serializer.validated_data.get('role')
        user = self.request.user

        if role == User.ROLE_ADMIN:
            # Сисадмин создает админа
            serializer.save(sysadmin=user)
        elif role == User.ROLE_WORKER:
            # Админ создает рабочего: указывает склад, но нужно убедиться, что это его склад
            warehouse = serializer.validated_data.get('warehouse')
            if warehouse and warehouse.admin != user:
                raise serializers.ValidationError("Вы можете добавлять работников только в свои склады.")
            serializer.save()
        else:
            serializer.save()


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return self.queryset.filter(admin=self.request.user)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_WORKER:
            return self.queryset.filter(warehouse=user.warehouse)
        if user.role == User.ROLE_ADMIN:
            return self.queryset.filter(warehouse__admin=user)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.ROLE_WORKER:
            serializer.save(warehouse=user.warehouse, created_by=user)
        else:
            serializer.save()


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_WORKER:
            return self.queryset.filter(warehouse=user.warehouse)
        if user.role == User.ROLE_ADMIN:
            return self.queryset.filter(warehouse__admin=user)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.ROLE_WORKER:
            serializer.save(warehouse=user.warehouse, created_by=user)
        else:
            serializer.save()


@api_view(['GET'])
@permission_classes([IsSysAdmin])
def sysadmin_dashboard(request):
    admins = User.objects.filter(role=User.ROLE_ADMIN, sysadmin=request.user)
    data = UserSerializer(admins, many=True).data
    return Response({'admins': data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    warehouse_id = request.query_params.get('warehouse_id')
    report_type = request.query_params.get('report_type')

    warehouses = Warehouse.objects.filter(admin=request.user)

    if warehouse_id:
        warehouses = warehouses.filter(id=warehouse_id)

    result = []
    for wh in warehouses:
        reports = wh.reports.all()
        if report_type:
            reports = reports.filter(type=report_type)

        result.append({
            'warehouse': WarehouseSerializer(wh).data,
            'workers': UserSerializer(wh.workers.all(), many=True).data,
            'videos': VideoSerializer(wh.videos.all(), many=True).data,
            'reports': ReportSerializer(reports, many=True).data,
        })

    return Response({'warehouses': result}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Укажите старый и новый пароль'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'error': 'Неверный старый пароль'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'success': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsWorker])
def worker_dashboard(request):
    wh = request.user.warehouse
    return Response({
        'warehouse': WarehouseSerializer(wh).data,
        'videos': VideoSerializer(wh.videos.all(), many=True).data,
        'reports': ReportSerializer(wh.reports.all(), many=True).data,
    }, status=status.HTTP_200_OK)
