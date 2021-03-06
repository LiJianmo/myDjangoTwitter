from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)

class UserSerializerWithProfile(UserSerializer):
    #user.profile.nickname
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(selfself, object):
        if object.profile.avatar:
            return object.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

class UserSerializerForTweet(UserSerializerWithProfile):
    pass

class UserSerializerForLike(UserSerializerWithProfile):
    pass

class UserSerializerForComment(UserSerializerWithProfile):
    pass

class UserSerializerForFriendship(UserSerializerWithProfile):
    pass

class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')



class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username does not exist.'
            })

        return data
class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=5)
    password = serializers.CharField(max_length=20, min_length=5)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This email address has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user

