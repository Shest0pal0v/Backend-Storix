from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, WarehouseViewSet,
    VideoViewSet, ReportViewSet,
    sysadmin_dashboard, admin_dashboard, worker_dashboard
)

router = DefaultRouter()
router.register(r'users',      UserViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'videos',     VideoViewSet)
router.register(r'reports',    ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/sysadmin/', sysadmin_dashboard),
    path('dashboard/admin/',     admin_dashboard),
    path('dashboard/worker/',    worker_dashboard),
]
