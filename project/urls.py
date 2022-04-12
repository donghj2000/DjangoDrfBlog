"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import TokenObtainPairView

from common.views import UserViewSet, UserLoginViewSet, UserLogoutViewSet, PasswordUpdateViewSet, ConstantViewSet, ImageUploadViewSet, ImageUpload, AccountResult
from blog.views import ArticleViewSet, ArticleArchiveListViewSet, TagViewSet, CatalogViewSet, CommentViewSet, LikeViewSet, MessageViewSet, NumberViewSet, TopArticleViewSet,ArticleSearchView

router = DefaultRouter()
router.register('user', UserViewSet,basename="user")
router.register('article', ArticleViewSet, basename="article")
router.register('archive', ArticleArchiveListViewSet, basename="archive")
router.register('tag', TagViewSet,basename="tag")
router.register('catalog', CatalogViewSet,basename="catalog")
router.register('comment', CommentViewSet,basename="comment")
router.register('like', LikeViewSet,basename="like")
router.register('message', MessageViewSet,basename="message")
router.register('number', NumberViewSet,basename="number")
router.register('top', TopArticleViewSet,basename="top")
# es
router.register("es", ArticleSearchView, basename = "article-search")


schema_view = get_schema_view(
    openapi.Info(
        title="Blog System API",
        description="Blog site ",
        default_version='v1',
        terms_of_service="",
        contact=openapi.Contact(email="XXXX@163.com"),
        license=openapi.License(name="GPLv3 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', include(router.urls)),
    path(r'account/result', AccountResult, name='result'),

    url(r'api/user/login', UserLoginViewSet.as_view()),
    url(r'api/user/logout', UserLogoutViewSet.as_view()),
    url(r'api/user/pwd', PasswordUpdateViewSet.as_view()),
    url(r'^dict', ConstantViewSet.as_view()),
    #url(r'upload/$', ImageUploadViewSet.as_view()),
    path('api/upload/<path:path>', ImageUpload),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico')),
    url(r'upload/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/jwt_login', obtain_jwt_token),
    # simple_jwt
    #path('api/jwt_login', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    #url('', include('social_django.urls', namespace='social')),
    re_path(
        r"api/swagger(?P<format>\.json|\.yaml)",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]