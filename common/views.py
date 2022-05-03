#!/usr/bin/env python
# encoding: utf-8

import logging
import django.conf
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login,logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import Constant
from common.models import User
from common.serializers import UserRegSerializer, UserDetailSerializer, UserLoginSerializer, UserPasswordSerializer
from common.utils import get_upload_file_path
from project.utils import send_email, get_sha256, get_current_site, generate_code
from common.tasks import sendMailTask


logger = logging.getLogger(__name__)

def get_random_password():
    import random
    import string
    return ''.join(random.sample(string.ascii_letters+string.digits, 8))

class BaseError(ValidationError):
    def __init__(self, detail=None, code=None):
        super(BaseError, self).__init__(detail={'detail':detail})

class BasePagination(PageNumberPagination):
    """
        customer pagination
    """
    # default page size
    page_size = 10
    # page size param in page size
    page_size_query_param = 'page_size'
    # page param in api
    page_query_param = 'page'
    # max page size
    max_page_size = 100


class BaseViewSetMixin(object):
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super(BaseViewSetMixin, self).__init__(**kwargs)
        self.filterset_fields = []
        self.init_filter_field()

    def init_filter_field(self):
        """
        Init filter field by the fields' intersection in model and serializer
        e.g. `book/?id=1&authors=2`
        :return:  None
        """
        serializer = self.get_serializer_class()
        if not hasattr(serializer, 'Meta'):
            return
        meta = serializer.Meta

        if not hasattr(meta, 'model'):
            return
        model = meta.model

        if not hasattr(meta, 'fields'):
            ser_fields = []
        else:
            ser_fields = meta.fields

        for field in ser_fields:
            if not hasattr(model, field):
                continue
            self.filterset_fields.append(field)

    def perform_update(self, serializer):
        user = self.fill_user(serializer, 'update')
        return serializer.save(**user)

    def perform_create(self, serializer):
        user = self.fill_user(serializer, 'create')
        return serializer.save(**user)

    @staticmethod
    def fill_user(serializer, mode):
        """
        before save, fill user info into para from session
        :param serializer: Model's serializer
        :param mode: create or update
        :return: None
        """
        request = serializer.context['request']
        user_id = request.user.id
        ret = {'modifier': user_id}

        if mode == 'create':
            ret['creator'] = user_id
        return ret

    def get_pk(self):
        if hasattr(self, 'kwargs'):
            return self.kwargs.get('pk')

    def is_reader(self):
        return isinstance(self.request.user, AnonymousUser) or not self.request.user.is_superuser


class BaseModelViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    pass

class UserViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend]
    queryset = User.objects.all().order_by('username')
    serializer_class = UserRegSerializer
    permission_classes = [permissions.AllowAny]

    def filter_queryset(self, queryset):
        queryset = super(UserViewSet, self).filter_queryset(queryset)
        #params = self.request.query_params
        #print(params)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_password = serializer.validated_data['password']
        user = self.perform_create(serializer)
        user.set_password(raw_password)
        user.is_active = False
        user.save()
        re_dict = serializer.data
        site = get_current_site().domain
        sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))

        if settings.DEBUG:
            site = '127.0.0.1:8000'
        path = reverse('result')
        url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
            site=site, path=path, id=user.id, sign=sign)
        #print(url)
        content = """
                        <p>请点击下面链接验证您的邮箱</p>
                        <a href="{url}" rel="bookmark">{url}</a>
                        再次感谢您！
                        <br />
                        如果上面链接无法打开，请将此链接复制至浏览器。
                        {url}
                        """.format(url=url)
        # print(content)

        try:
            """
            send_mail(subject="验证您的电子邮箱",
                    message=content,
                    from_email=django.conf.settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False)
            """
            sendMailTask.delay(subject="验证您的电子邮箱",
                    message=content,
                    recipient_list=[user.email])
                    
            re_dict["detail"] = "向你的邮箱发送了一封邮件，请打开验证，完成注册。"
        except Exception as e:
            print(e)
            re_dict["detail"] = "发送验证邮箱失败，请检查邮箱是否正确。"

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        if self.action == "create":  #注册用户不需要权限
            return []
        if self.action == "partial_update": 
            if self.request.data.get("is_active","no") != "no": #启用或禁用用户时需要管理员权限
                return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticated()]
 
    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == "create":
                return UserRegSerializer
        return UserDetailSerializer   
    
    def perform_create(self, serializer): # 注册用户时不填user_id，因此重写这个函数，覆盖BaseViewSetMixin中的那一个
        return serializer.save()
      

class UserLoginViewSet(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        # for test serializer class
        #print(request.data)
        #serializer = self.get_serializer(data=request.data)
        #serializer.is_valid(raise_exception=True)
        #print(serializer.validated_data)
        
        users = User.objects.filter(username=username)
        user: User = users[0] if users else None
        if user is None:
            return Response({'detail': '用户不存在。'}, status=status.HTTP_200_OK)
        if not user.is_active:
            return Response({'detail': '账号未激活，请登录邮箱激活。'}, status=status.HTTP_200_OK)
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                serializer = UserDetailSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            ret = {'detail': '密码错误或验证失败。'}
            return Response(ret, status=status.HTTP_200_OK)

class UserLogoutViewSet(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return Response({'detail': 'logout successful!'})

class PasswordUpdateViewSet(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPasswordSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        password = request.data.get('password', '')
        new_password = request.data.get('new_password', '')
        user = User.objects.get(id=user_id)
        if not user.check_password(password):
            ret = {'detail': 'old password is wrong !'}
            return Response(ret, status.HTTP_403_FORBIDDEN)

        user.set_password(new_password)
        user.save()
        return Response({
			'detail': 'password changed successful'
		})
    def put(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        users = User.objects.filter(username=username)
        user: User = users[0] if users else None

        if user is not None:
            if not user.is_active:
                return Response({'detail': '账号未激活.'})
            password = get_random_password()
            print('password:' + password)
            print(user.email)
            try:
                """
                send_mail(subject="您在博客VueBlog上的新密码",
                          message="Hi: 你的新密码: \n{}".format(password),
                          from_email=django.conf.settings.EMAIL_HOST_USER,
                          recipient_list=[user.email],
                          fail_silently=False)
                """
                sendMailTask.delay(subject="您在博客VueBlog上的新密码",
                          message="Hi: 你的新密码: \n{}".format(password),
                          recipient_list=[user.email])
                    
                user.password= make_password(password)
                user.save()
                return Response({'detail': '新密码已经发送到你的邮箱。'})
            except Exception as e:
                print(e)
                return Response({'detail': 'Send New email failed, Please check your email address'})
        else:
            ret = {'detail': '账号不存在。'}
            return Response(ret, status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if self.request._request.method == "POST":
            return [permissions.IsAuthenticated()]
        else:
            return [permissions.AllowAny()]

class ConstantViewSet(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPasswordSerializer
    queryset = QuerySet()

    def get(self, request, *args, **kwargs):
        ret = {}
        for key in dir(Constant):
            if not key.startswith("_"):
                ret[key] = getattr(Constant, key)
        return Response(ret)


class ImageUploadViewSet(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            if request.method == 'POST' and request.FILES:
                uploaded_file = request.FILES['file']
                #print(uploaded_file.name)
                full_file_path, file_path = get_upload_file_path(uploaded_file.name)
                self.handle_uploaded_file(uploaded_file, full_file_path)

                return Response({ 'url': file_path })

        except Exception as e:
            logging.getLogger('default').error(e, exc_info=True)
            raise BaseError(detail='Upload failed', code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def handle_uploaded_file(f, file_path):
        destination = open(file_path, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

def handle_uploaded_file(f, file_path):
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
        destination.close()
def ImageUpload(request, path):
    try:
        if request.method == 'POST' and request.FILES:
            uploaded_file = request.FILES['file']
            #print("ImageUpload,")
            #print(path)
            #print(uploaded_file.name)
            full_file_path, file_path = get_upload_file_path(path,uploaded_file.name)
            handle_uploaded_file(uploaded_file, full_file_path)

            response = {
                'url': file_path
            }
            return JsonResponse(response)
        else:
            BaseError(detail='Upload failed', code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logging.getLogger('default').error(e, exc_info=True)
        raise BaseError(detail='Upload failed', code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def AccountResult(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)
    if user.is_active:
        return HttpResponse("已经验证成功，请登录。")
        
    if type and type == 'validation':
        c_sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
        sign = request.GET.get('sign')
        if sign != c_sign:
            return HttpResponse("验证失败。")
        user.is_active = True
        user.save()
        return HttpResponse("验证成功。恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站")
    else:
        return HttpResponse("验证成功。")

from django.utils import timezone
def my_jwt_response_payload_handler(token, user=None, request=None):
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    return {
        'expire_days': settings.JWT_EXPIRE_DAYS,
        'token': token,
        'user': UserDetailSerializer(user, context={'request': request}).data
    }
