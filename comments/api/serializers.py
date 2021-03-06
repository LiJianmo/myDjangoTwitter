from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet
from likes.services import LikeService

class CommentSerializer(serializers.ModelSerializer):
    #因为引用到了user 所以特殊分配一下，
    # 如果不加的话，会以user_id形式来显示，
    # 现在serializer套serializer，会把user做成新的hashmap
    user = UserSerializerForComment(source='cached_user')
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'likes_count',
            'has_liked',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_likes_count(self, obj):
        return obj.like_set.count()

class CommentSerializerForCreate(serializers.ModelSerializer):
    # 这两项必须手动添加
    # 因为默认 ModelSerializer 里只会自动包含 user 和 tweet 而不是 user_id 和 tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({
                'message': 'tweet does not exist'
            })
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )

class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', )

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()

        return instance