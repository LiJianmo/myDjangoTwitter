from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerForDetail
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService


# Create your views here.
#白名单 gen添加create和list，用modelviewset会权限太多了不合适，但其实不加就可以 因为是自己实现的后面
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin,
                   ):
    #可有可无了 因为methods里面不用queryset，没有get_queryset
    queryset = Tweet.objects.all()
    #指定他的serializer，决定了创建的时候 默认的表单长什么样子
    serializer_class = TweetSerializerForCreate
    filterset_fields = {'user_id', }

    pagination_class = EndlessPagination


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            #equal 没有 允许任何人访问
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        #if no user in
        user_id = request.query_params['user_id']
        #
        # queryset = self.get_queryset()
        # tweets = TweetService.get_cached_tweets(user_id=user_id)
        # #comments = self.filter_queryset(queryset).order_by('created_at')
        # # user_id = request.query_params['user_id']
        # # tweets = Tweet.objects.filter(
        # #     user_id = user_id).order_by('-created_at')
        # #will return "list of dict" 每个list是serializer.data
        # #tweets is queryset
        #
        # #现在tweets是一个ordered list了，对ordered list进行pagination
        # #这里用的是我们自己的endlesspagination中的paginate_queryset方法，
        # #因为之前定义了pagination_class = EndlessPagination
        # tweets = self.paginate_queryset(tweets)


        cached_queryset = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_queryset, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)

        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True,

        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <HOMEWORK 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        #这里用到了get_object 所以要定义一下之前的queryset
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(
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
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet, context={'request': request}).data,
                        status=201,
        )