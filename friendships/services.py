from friendships.models import Friendship
from django.contrib.auth.models import User

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

