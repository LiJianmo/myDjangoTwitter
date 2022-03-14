from accounts.models import UserProfile
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches
from twitter.cache import USER_PROFILE_PATTERN, USER_PATTERN
from utils.memcached_helper import MemcachedHelper


cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    # @classmethod
    # def get_user_through_cache(cls, user_id):
    #     key = USER_PATTERN.format(user_id=user_id)
    #     #read from cache
    #     user = cache.get(key)
    #     if user is not None:
    #         return user
    #
    #     #doesn't exist in cache, read from db
    #     try:
    #         user = User.objects.get(id=user_id)
    #         #add to cache
    #         cache.set(key, user)
    #     except User.DoesNotExist:
    #         user=None
    #
    #     return user
    #
    # @classmethod
    # def invalidate_user(cls, user_id):
    #     key = USER_PATTERN.format(user_id=user_id)
    #     cache.delete(key)

    @classmethod
    def get_user_by_id(cls, user_id):
        return MemcachedHelper.get_object_through_cache(User, user_id)

    @classmethod
    def get_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)

        profile = cache.get(key)

        if profile is not None:
            print(profile.user)
            return profile

        profile,_ = UserProfile.objects.get_or_create(user_id=user_id)
        print("here is profile info ")
        print(profile.user)
        cache.set(key, profile)

        return profile


    @classmethod
    def invalidate_profile(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
