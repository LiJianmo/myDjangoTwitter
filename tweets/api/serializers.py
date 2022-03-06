from tweets.models import Tweet
from rest_framework import serializers
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)



class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    #comments = serializers.SerializerMethodField()
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'comments',
            'created_at',
            'content',
            'likes',
            'comments',
            'likes_count',
            'comments_count',
            'has_liked',
        )

    # def get_comments(self, object):
    #     return CommentSerializer(object.comment_set.all(), many=True).data

class TweetCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=5, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content', )

    def create(self, validated_data):
        #use context to store request
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(
            user=user,
            content=content,
        )
        return tweet