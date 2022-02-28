from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService

class NewsfeedService(object):
    @classmethod
    def fanout_to_followers(cls, tweet):
        #对所有的followers 在newsfeed中create一下 传参数user和tweet
        #这种多次create 用bulk create
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]

        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)


