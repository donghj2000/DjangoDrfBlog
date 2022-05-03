from rest_framework import serializers
from common.models import User
from rest_framework.validators import UniqueValidator

class UserRegSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])
    #输入密码的时候不显示明文
    password = serializers.CharField(
        style={'input_type': 'password'},label='密码',write_only=True
    )
    class Meta:
        model = User
        fields = ['id', 'username','password', 'last_login', 'avatar', 'email', 'is_active', 'created_at',  'nickname','is_superuser', 'desc']

class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'avatar', 'email', 'is_active', 'created_at',  'nickname','is_superuser', 'desc']
        extra_kwargs = {
            'id': { 'read_only': True},
            'username': { 'read_only': True},
            'last_login': { 'read_only': True},
            #'is_active': { 'read_only': True},
            'created_at': { 'read_only': True},
            'is_superuser': { 'read_only': True},
        }

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': { 'write_only': True},
        }

class UserPasswordSerializer(serializers.ModelSerializer):
    #new_password=serializers.SerializerMethodField()
    new_password = serializers.CharField(max_length=128, min_length=8, allow_blank=False, trim_whitespace=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'new_password'] # username

    #def get_new_password(obj):
    #    return obj.password or ''