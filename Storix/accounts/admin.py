# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Warehouse, Video, Report

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    model = User
    # поля, которые вы сможете сразу увидеть в списке пользователей
    list_display = (
        'username', 'email', 'role', 'sysadmin', 'warehouse',
        'is_staff', 'is_active'
    )
    list_filter = ('role', 'is_staff', 'is_active')
    # дополняем стандартный набор полей вашими
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Доп. поля по роли', {
            'fields': ('role', 'sysadmin', 'warehouse'),
        }),
    )
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        ('Доп. поля по роли', {
            'classes': ('wide',),
            'fields': ('role', 'sysadmin', 'warehouse'),
        }),
    )

# регистрируем остальные модели
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin')
    list_filter  = ('admin',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'created_by', 'upload_time')
    list_filter  = ('warehouse',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'created_by', 'discrepancies_count', 'created_at')
    list_filter  = ('warehouse',)

