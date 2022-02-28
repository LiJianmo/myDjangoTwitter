from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship

from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
# Create your views here.
class FriendshipViewSets(viewsets.GenericViewSet):
    queryset = User.objects.all()
    #post action会寻找serializer_class 或者get_serializer_class
    serializer_class = FriendshipSerializerForCreate

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(
            to_user_id=pk
        ).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    #TO_USER 变成from_user
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(
            from_user_id=pk
        ).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    #follow api post create record
    #基于某个用户，则detail=True
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        #verify if exist
        #静默处理
        if Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).exists():
            return Response({
                'success': True,
                'duplicate': True
            }, status=status.HTTP_201_CREATED)

        #check if to_user exists
        to_user = self.get_object()

        serializer = FriendshipSerializerForCreate(
            data={
                'from_user_id': request.user.id,
                'to_user_id': to_user.id,
            }
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(FollowingSerializer(instance).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted,_ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()

        return Response({
            'success': True,
            'deleted': deleted
        })


    def list(self, request):
        return Response({'message': "this is friendships home page"})

