from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet

# Create your models here.
class NewsFeed(models.Model):

    #one user to store who can see this tweet
    #one tweet
    #created_at in order to quickly sort
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



