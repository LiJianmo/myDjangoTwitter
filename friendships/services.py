from friendships.models import Friendship
from django.contrib.auth.models import User

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        #或者用prefetch_related 可以变两条 1.取friendship 2.取id查询
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id_in = follower_ids)

        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')

        return [friendship.from_user for friendship in friendships]