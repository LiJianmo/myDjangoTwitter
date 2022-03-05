from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
#from comments.models import Comment

# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    #define index_together add class meta
    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    # @property
    # def comments(self):
    #     return self.comment_set.all()
    #     return Comment.objects.filter(tweet=self)

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'