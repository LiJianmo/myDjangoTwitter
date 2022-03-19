from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper

class NewsFeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        #对所有的followers 在newsfeed中create一下 传参数user和tweet
        #这种多次create 用bulk create
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]

        #the tweet owner needs to see as well
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))

        NewsFeed.objects.bulk_create(newsfeeds)

        #手动 for 进cache
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)


    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        #user_id和user.id 区别在user_id可以直接从newsfeed的model中拿到
        #user.id就会造成新的DB查询请求
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_objects(key, newsfeed, queryset)

