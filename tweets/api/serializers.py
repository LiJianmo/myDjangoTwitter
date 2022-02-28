from tweets.models import Tweet
from rest_framework import serializers
from accounts.api.serializers import UserSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')

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