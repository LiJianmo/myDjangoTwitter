from friendships.models import Friendship
from django.contrib.auth.models import User
from django.core.cache import caches
from django.conf import settings
from twitter.cache import FOLLOWINGS_PATTERN



cache = caches['testing'] if settings.TESTING else caches['default']



class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        #或者用prefetch_related 可以变两条 1.取friendship 2.取id查
        # 正确的写法一，自己手动 filter id，使用 IN Query 查询
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        #.from_user_id 不会产生新的sql查询,本身存在table里面
        # followers = User.objects.filter(id__in=follower_ids)

        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')

        return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        # get data from mamcached , 1 get key
        # we don't cache followers since 1.the amount is very big 2.they often update

        # LRU least recently used 淘汰机制 key

        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        #memcached cache
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            friendship.to_user_id
            for friendship in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set


    @classmethod
    def invalidate_foollowing_cache(cls, from_user_id):
        #delete the key directly
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)