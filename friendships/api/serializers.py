from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from friendships.services import FriendshipService


class FollowingUserIdSetMixin:
    #now this is a property
    #we will have many serializer instances but we
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        #oject level cache, if in this cache return directly
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        #if not in cache, just call filter to get following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        #after getting user_id_set, set it into cache
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set



#follower 粉丝，一般不会存在cache中因为太多太容易更新了
class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    #一般是UserSerializerForFriendship 但现在就是去model中 找Friendship中的from_user内容
    user = UserSerializerForFriendship(source='cached_from_user')
    #可以不用有默认
    created_at = serializers.DateTimeField()

    has_followed = serializers.SerializerMethodField()


    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, object):
        # if self.context['request'].user.is_anonymous:
        #     return False

        #from_user: 当前登录的user 即self.context['request'].user
        #to_user: 关注xx的user xx是object from_user是xx的follower（粉丝）
        #but every object nedds to be check by sql
        #return FriendshipService.has_followed(self.context['request'].user, object.from_user)

        return object.from_user_id in self.following_user_id_set






class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    created_at = serializers.DateTimeField()

    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, object):
        # if self.context['request'].user.is_anonymous:
        #     return False

        #return FriendshipService.has_followed(self.context['request'].user, object.to_user)
        return object.to_user_id in self.following_user_id_set






class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'cannot follow yourself',
            })
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'already followed',
            })
        if not User.objects.filter(id = attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'cannot follow a non-exist user',
            })

        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
