from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet

# Create your views here.
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin,
                   ):
    #可有可无了 因为methods里面不用queryset
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            #equal 没有 允许任何人访问
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        #if no user in
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(
            user_id = user_id).order_by('-created_at')
        #will return "list of dict" 每个list是serializer.data
        #tweets is queryset
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = TweetCreateSerializer(
            #use context to store request, when running serializer.save(),
            #the create method would be called, and we could get user info from request
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)