from rest_framework import serializers
from .models import User, Warehouse, Video, Report

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'sysadmin', 'warehouse']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'admin']
        read_only_fields = ['id']

class VideoSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'warehouse', 'created_by', 'file_path', 'upload_time']
        read_only_fields = ['id', 'created_by', 'upload_time']

class ReportSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'warehouse', 'created_by', 'discrepancies_count', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
