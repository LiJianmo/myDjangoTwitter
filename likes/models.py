from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from accounts.services import UserService

from utils.memcached_helper import MemcachedHelper

# Create your models here.

class Like(models.Model):
    #记录点赞的主体(tweet or comment)
    object_id = models.PositiveIntegerField()
    #区分点赞的是comment还是tweet
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'), )
        index_together = (('user', 'content_type', 'object_id', 'created_at'), )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )


    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)
    #如果希望得到一些便利的时候，就写在model中，和model自身有关，不带什么参数，property属性，
    # 如果太长，也要包进service中
    #user = UserSerializerForLike(source='cached_user')