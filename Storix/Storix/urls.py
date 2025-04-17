from django.contrib import admin
from django.urls import path, include
# JWT views для получения и обновления токенов
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Для отдачи вашего frontend-шаблона
from django.views.generic import TemplateView

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),

    # JWT: получить пару токенов (access + refresh)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # JWT: обновить access по refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # DRF Browsable API login/logout
    path('api-auth/', include('rest_framework.urls')),

    # Основные CRUD‑роуты вашего приложения
    path('api/', include('accounts.urls')),

    # SPA / фронтенд
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
