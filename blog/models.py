import mptt.models
from django.db import models

from common.constants import Constant
from common.models import AbstractBaseModel, User


class Tag(AbstractBaseModel):
    name = models.CharField('标签名称', max_length=50, unique=True, null=False, blank=False)

    class Meta:
        db_table = 'blog_tag'

    def __str__(self):
        return self.name


class Catalog(mptt.models.MPTTModel, AbstractBaseModel):
    name = models.CharField('分类名称', max_length=50, unique=True, null=False, blank=False)
    parent = mptt.models.TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='children')
    class Meta:
        db_table = 'blog_catalog'

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Article(AbstractBaseModel):
    title = models.CharField('文章标题', max_length=100, unique=True, null=False, blank=False)
    cover = models.TextField('封面', max_length=1000, blank=True)
    excerpt = models.CharField('摘要', max_length=200, blank=True)
    keyword = models.CharField('关键词', max_length=200, blank=True)
    markdown = models.TextField('正文', max_length=100000, null=False, blank=False)
    status = models.CharField('文章状态', max_length=30, choices=Constant.ARTICLE_STATUS,
                              default=Constant.ARTICLE_STATUS_DRAFT)
    catalog = models.ForeignKey(Catalog, verbose_name='所属分类', null=False, blank=False,
                                on_delete=models.DO_NOTHING, related_name='cls_articles')
    tags = models.ManyToManyField(Tag, verbose_name='文章标签', blank=True, related_name='tag_articles')

    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.DO_NOTHING, null=False, blank=False)
    views = models.PositiveIntegerField('浏览量', default=0, editable=False)
    comments = models.PositiveIntegerField('评论数量', default=0, editable=False)
    likes = models.PositiveIntegerField('点赞量', default=0, editable=False)
    words = models.PositiveIntegerField('字数', default=0, editable=False)

    class Meta:
        db_table = 'blog_article'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Like(AbstractBaseModel):
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING, related_name='article_likes')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='like_users')

    class Meta:
        db_table = 'blog_like'


class Comment(AbstractBaseModel):
    article = models.ForeignKey(Article, verbose_name='评论文章', on_delete=models.DO_NOTHING,
                                related_name='article_comments')
    user = models.ForeignKey(User, verbose_name='评论者', on_delete=models.DO_NOTHING, related_name='comment_users')
    reply = models.ForeignKey('self', verbose_name='评论回复', on_delete=models.CASCADE, related_name='comment_reply',
                              null=True, blank=True)
    content = models.TextField('评论', max_length=10000, null=False, blank=False)

    class Meta:
        db_table = 'blog_comment'


class Message(AbstractBaseModel):
    email = models.EmailField('邮箱', max_length=100, null=False, blank=False)
    content = models.TextField('内容', max_length=10000, null=False, blank=False)
    phone = models.CharField('手机', max_length=20, null=True, blank=True)
    name = models.CharField('姓名', max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'blog_message'