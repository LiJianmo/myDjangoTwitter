from django.db import models
from django.contrib.auth.models import User



# save之后 delete之前 加上两个监听
from django.db.models.signals import post_save, pre_delete
from friendships.listeners import invalidate_following_cache

from utils.memcached_helper import MemcachedHelper

# Create your models here.
class Friendship(models.Model):
    #粉丝
    from_user = models.ForeignKey(
        User,
        #on_delete会帮助我们在delete的时候不是真的删除而是变成null
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_friendship_set",
    )

    to_user = models.ForeignKey(
        User,
        # on_delete会帮助我们在delete的时候不是真的删除而是变成null
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_friendship_set",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together=(
            #get all following users of curr user
            ('from_user_id', 'created_at'),
            #get all users I followed
            ('to_user_id', 'created_at'),
        )

        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return '{} followed {}'.format(self.from_user_id, self.to_user_id)


    @property
    def cached_from_user(self):
        from accounts.services import UserService
        return MemcachedHelper.get_object_through_cache(User, self.from_user_id)

    @property
    def cached_to_user(self):
        from accounts.services import UserService
        return MemcachedHelper.get_object_through_cache(User, self.to_user_id)


#
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)
