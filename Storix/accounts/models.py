from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    # Переопределяем группы и права, чтобы не конфликтовать с auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='accounts_user_set'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='accounts_user_permissions_set'
    )

    ROLE_SYSADMIN = 'sysadmin'
    ROLE_ADMIN    = 'admin'
    ROLE_WORKER   = 'worker'

    ROLE_CHOICES = [
        (ROLE_SYSADMIN, 'System Administrator'),
        (ROLE_ADMIN,    'Administrator'),
        (ROLE_WORKER,   'Worker'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_WORKER,
        help_text="Role of the user"
    )

    sysadmin = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': ROLE_SYSADMIN},
        related_name='admins'
    )

    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workers'
    )

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_ADMIN},
        related_name='warehouses'
    )

    def __str__(self):
        return self.name

class Video(models.Model):
    warehouse   = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='videos')
    created_by  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': User.ROLE_WORKER},
        related_name='videos_created'
    )
    file_path   = models.FileField(upload_to='videos/')
    upload_time = models.DateTimeField(auto_now_add=True)
    video_data  = models.BinaryField()

    def __str__(self):
        return f"Video {self.pk} by {self.created_by}"

class Report(models.Model):
    warehouse           = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reports')
    created_by          = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': User.ROLE_WORKER},
        related_name='reports_created'
    )
    discrepancies_count = models.PositiveIntegerField()
    file_data           = models.BinaryField()
    created_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.pk} by {self.created_by}"
