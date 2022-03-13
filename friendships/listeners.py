def invalidate_following_cache(sender, instance, **kwargs):
    #instance 被保存或者删除的那一个friendship
    #
    from friendships.services import FriendshipService
    FriendshipService.invalidate_foollowing_cache(instance.from_user_id)

