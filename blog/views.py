import datetime

from common.utils import get_year
from django.db.models import QuerySet, Sum, Count
from rest_framework import mixins, permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from blog.models import Article, Comment, Message, Tag, Catalog,Like
from blog.serializers import ArticleSerializer, CommentSerializer, MessageSerializer, TagSerializer, \
    ArticleListSerializer, CatalogSerializer, LikeSerializer, ArticleIndexSerializer
from common.constants import Constant
from common.views import BaseModelViewSet, BaseViewSetMixin, BasePagination
# 1
class ArticleArchiveListViewSet(BaseViewSetMixin, mixins.ListModelMixin, GenericViewSet):
    pagination_class = BasePagination
    queryset = Article.objects.all().order_by('id') #也可以按照 created_at 排序，理论上这两个字段的递增顺序是一致的
    serializer_class = ArticleListSerializer
  
    def filter_queryset(self, queryset)->QuerySet:
        queryset = super(ArticleArchiveListViewSet, self).filter_queryset(queryset)
        if self.is_reader():
            queryset = queryset.exclude(status=Constant.ARTICLE_STATUS_DRAFT)
        return queryset.exclude(status=Constant.ARTICLE_STATUS_DELETED)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            total = len(queryset)
            ret = {
                "count": total,
                "next": None,
                "previous": None,
                'results': []
            }
            if total != 0:
                # page_size, page_number=self.get_page_info()
                # start_year, end_year = self.get_datetime_range(page_size, page_number)
                # queryset = queryset.filter(created_at__gte=start_year).filter(created_at__lt=end_year)
                years = {}
                for article in page:
                    year = article.created_at.year
                    articles = years.get(year)
                    if not articles:
                        articles = []
                        years[year] = articles
                    serializer = self.get_serializer(article)
                    articles.append(serializer.data)
                
                for key, value in years.items():
                    ret['results'].append({
                        'year': key,
                        'list': value
                    })
                ret['results'].sort(key=lambda i:i['year'], reverse=True)
            
        return Response(ret)

    # def get_page_info(self):
    #     page_size = self.paginator.get_page_size(self.request)
    #     page_number = self.request.query_params.get(self.paginator.page_query_param, 1)
    #     return page_size, int(page_number)
    # @staticmethod
    # def get_datetime_range(page_size, page_number):
    #    current_year = get_year(datetime.datetime.now())
    #    start_year = current_year - page_size * page_number + 1
    #    start_datetime = '{:d}-01-01 00:00:00'.format(start_year)
    #    end_datetime = '{:d}-01-01 00:00:00'.format(start_year + page_size)
    #    return start_datetime, end_datetime
# 1
class ArticleViewSet(BaseModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Article.objects.all().select_related('catalog', 'author')
    serializer_class = ArticleListSerializer
    #前端搜索字段名字为 search,在restframework/settings.py里有配置，因此前端代码要跟这里一致    
    # 'SEARCH_PARAM': 'search',
    # 'ORDERING_PARAM': 'ordering',
    filter_backends = (DjangoFilterBackend,filters.SearchFilter)
    search_fields = ('title',)

    def filter_queryset(self, queryset):
        #self.filterset_fields.remove('catalog')
        queryset = super(ArticleViewSet, self).filter_queryset(queryset)
        if self.is_reader():
            queryset = queryset.exclude(status=Constant.ARTICLE_STATUS_DRAFT).exclude(
                status=Constant.ARTICLE_STATUS_DELETED)
        # print(len(queryset))
        params = self.request.query_params
        # page_size = self.paginator.get_page_size(self.request)
        # page_number = self.request.query_params.get(self.paginator.page_query_param, 1)
        # print(params)
        
        if 'catalog' in params:
            print('has catalog')
            catalog_id = params.get('catalog', 1)
            catalog = Catalog.objects.get(id=catalog_id)
            catalogs = catalog.get_descendants(include_self=True)
            queryset = queryset.filter(catalog__in=[c.id for c in catalogs])
        print("ArticleView len(queryset) 2")
        print(len(queryset))
        return queryset

    def perform_create(self, serializer):
        extra_infos = self.fill_user(serializer,'create')
        extra_infos['author'] = self.request.user
        serializer.save(**extra_infos)

    def perform_destroy(self, instance: Article):
        instance.status = Constant.ARTICLE_STATUS_DELETED
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        instance: Article = self.get_object()
        serializer = self.get_serializer(instance)
        if self.is_reader():
            instance.views += 1
            instance.save()
        return Response(serializer.data)

    def perform_update(self, serializer):
        extra_infos = self.fill_user(serializer, 'update')
        serializer.save(**extra_infos)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == "list":
                return ArticleListSerializer
        return ArticleSerializer

    def get_permissions(self):
        if self.action == "create" or self.action == "update" or self.action == "partial_update":
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]

# 1
class CommentViewSet(BaseModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('content',)
    
    def filter_queryset(self, queryset):
        print("CommentView filter")
        print(len(queryset))
        queryset = super(CommentViewSet, self).filter_queryset(queryset)
        #queryset = queryset.filter(reply__isnull=True)
        print(len(queryset))
        return queryset

    def perform_create(self, serializer):
        super(CommentViewSet, self).perform_create(serializer)
        article: Article = serializer.validated_data['article']
        article.comments += 1
        article.save()
#1
class LikeViewSet(BaseModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        super(LikeViewSet, self).perform_create(serializer)
        article: Article = serializer.validated_data['article']
        article.likes += 1
        article.save()
#1
class MessageViewSet(BaseModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = (DjangoFilterBackend,filters.SearchFilter)
    search_fields = ('name', 'email', 'phone', 'content')

# 1
class TagViewSet(BaseModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
# 1
class CatalogViewSet(BaseModelViewSet):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer

    def list(self, request, *args, **kwargs):
        ret = []
        roots = Catalog.objects.filter(id=1).filter(parent__isnull=True)
        if not roots:
            return Response(ret)
        root: Catalog = roots[0]
        root_dict = CatalogSerializer(root).data
        root_dict['children'] = []
        ret.append(root_dict)
        parent_dict = {root.id:root_dict}
        for cls in root.get_descendants():
            data = CatalogSerializer(cls).data
            parent_id = data.get('parent')
            parent = parent_dict.get(parent_id)
            parent['children'].append(data) 

            if not cls.is_leaf_node() and cls.id not in parent_dict:
                data['children'] = []
                parent_dict[cls.id] = data
        return Response(ret)
#1
class NumberViewSet(BaseViewSetMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().aggregate(Sum('views'), Sum('likes'), Sum('comments'))
        messages = Message.objects.aggregate(Count('id'))
        return Response({
            'views': queryset['views__sum'],
            'likes': queryset['likes__sum'],
            'comments': queryset['comments__sum'],
            'messages': messages['id__count']
        })
#1
class TopArticleViewSet(NumberViewSet):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-views')[:10]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# elastic search 
from drf_haystack.viewsets import HaystackViewSet
class ArticleSearchView(HaystackViewSet):
    index_models = [Article]
    serializer_class = ArticleIndexSerializer
    pagination_class = BasePagination
