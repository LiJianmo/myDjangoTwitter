from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet

from utils.memcached_helper import MemcachedHelper

from newsfeeds.listeners import push_newsfeed_to_cache
from django.db.models.signals import post_save, pre_delete

# Create your models here.
class NewsFeed(models.Model):

    #one user to store who can see this tweet
    #one tweet
    #created_at in order to quickly sort
    #user指的是这个user可以看到这些tweets，
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True,)
    created_at = models.DateTimeField(auto_now_add=True,)

    class Meta:
        index_together = (('user', 'created_at'), )
        #联合约束 保证user_id+tweet_id唯一性
        unique_together = (('user', 'tweet'), )
        ordering = ('user', '-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user} : {self.tweet}'


    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)






    #newsfeeds 的创建,not only through create, but also bulk create method.
    #following: get_all_following 获取我自己关注的所有博主， from_user
    #follower : get_all_follower 获取我的所有粉丝们  to_user
    #fanout_to_followers : 对于我所有的粉丝们（followers），我们做一个list of newsfeeds，
    # 里面存newsfeed：1.user=follower（粉丝），这表示的是粉丝们可以观看 2. tweet
    #bulk create 不能触发listener中的signal，只能自己写触发机制了



post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)

#newsfeed会被fanout给所有的粉丝
#所以对于明星用户，我们不用fanout机制，做pull的机制，要不然会挺大的影响缓存
#然后可以优化，通过不存储tweets的内容，存储tweets的id