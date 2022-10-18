from rest_framework import serializers
from blog.models import Catalog, Tag, Article, Like, Message, Comment

class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = ['id', 'name', 'parent']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at', 'modified_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }

class ArticleListSerializer(serializers.ModelSerializer):
    tags_info = serializers.SerializerMethodField(read_only = True)
    catalog_info = serializers.SerializerMethodField(read_only=True)
    #status = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'excerpt', 'cover', 'created_at', 'modified_at', 'tags',
                  'tags_info', 'catalog', 'catalog_info', 'views', 'comments', 'words', 'likes', 'status', ]
        
        extra_kwargs = {
            'tags': {'write_only': True},
            'catalog': {'write_only': True},
            'views': {'read_only': True},
            'comments': {'read_only': True},
            'words': {'read_only': True},
            'likes': {'read_only': True},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }
        
    @staticmethod
    def get_tags_info(obj: Article) -> list:
        if not obj.title:
            article = Article.objects.get(id=obj.id)
            tags = article.tags.all()
        else:
            tags = obj.tags.all()
        return [{'id': tag.id, 'name': tag.name} for tag in tags]

    @staticmethod
    def get_catalog_info(obj: Article)->dict:
        if not obj.catalog:
            book = Article.objects.get(id=obj.id)
            catalog = book.catalog
        else:
            catalog = obj.catalog
        return {
            'id': catalog.id,
            'name': catalog.name,
            'parents': [c.id for c in catalog.get_ancestors(include_self=True)]
        }
    # @staticmethod
    # def get_status(obj:Article)->list:
    #     status = obj.get_status_display()
    #     return status

class ArticleSerializer(ArticleListSerializer):
    class Meta(ArticleListSerializer.Meta):
        fields = ['markdown', 'keyword']
        fields.extend(ArticleListSerializer.Meta.fields)

class LikeSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField(read_only=True)
    article_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Like
        fields = ['user', 'user_info', 'article', 'article_info', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
    @staticmethod
    def get_user_info(obj: Like)->dict:
        if not obj.user:
            return {}
        else:
            user = obj.user
        return {'id': user.id, 'name': user.nickname or user.username, 'avatar': user.avatar}

    @staticmethod
    def get_article_info(obj: Like)->dict:
        if not obj.article:
            return {}
        else:
            article = obj.article
        return {'id': article.id, 'title':article.title}

class CommentSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField(read_only=True)
    article_info = serializers.SerializerMethodField(read_only=True)
    comment_replies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_info', 'article', 'article_info', 'created_at', 'reply', 'content',
                    'comment_replies']
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
    @staticmethod
    def get_user_info(obj:Comment)->dict:
        if not obj.user:
            return {}
        else:
            user = obj.user
        return {
            'id': user.id, 
            'name': user.nickname or user.username, 
            'avatar': user.avatar,
            'role': "Admin" if user.is_superuser  else "",
            }
    @staticmethod
    def get_article_info(obj:Comment)->dict:
        if not obj.article:
            return {}
        else:
            article = obj.article
        return {'id': article.id, 'title': article.title}

    def getReplies(self,replies):
        comment_replies = []
        if len(replies)==0:
            return []
        for reply in replies:
            if reply.user != None:
                comment_replies.append({
                    "id":              reply.id,
                    "content":         reply.content,
                    "user_info":       {
                                        "id":     reply.user.id,
                                        "name":   reply.user.nickname or reply.user.username,
                                        "avatar": reply.user.avatar,   
                                        "role":   "Admin" if reply.user.is_superuser else "" 
                                    },
                    "created_at":      reply.created_at,
                    "comment_replies": self.getReplies(reply.comment_reply.all()) })
        return comment_replies 

    def get_comment_replies(self, obj: Comment):
        if not obj.comment_reply:
            return []
        else:
            replies = obj.comment_reply.all()

        return [{
            'id': reply.id,
            'content': reply.content,
            'user_info': {
				'id': reply.user.id,
                'name': reply.user.nickname or reply.user.username,
                'avatar': reply.user.avatar,   
                'role': "Admin" if reply.user.is_superuser  else "",
            },
            'created_at': reply.created_at,
            "comment_replies": self.getReplies(reply.comment_reply.all())
        } for reply in replies]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'email', 'phone', 'name', 'content', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
        }

# elastic search 
from drf_haystack.serializers import HaystackSerializer
from blog.search_indexes import ArticleIndex

class ArticleIndexSerializer(HaystackSerializer):
    object = ArticleSerializer(read_only=True)

    class Meta:
        index_classes = [ArticleIndex]
        fields = ('text', 'object')
