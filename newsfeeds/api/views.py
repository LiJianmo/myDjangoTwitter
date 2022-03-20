from django.shortcuts import render
from rest_framework import viewsets, status
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService

# Create your views here.
class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    pagination_class = EndlessPagination

    def list(self, request):
        #NewsFeedSerializer需要的参数就是一个有关newsfeed的queryset
        # query = NewsFeed.objects.filter(user=self.request.user)

        cached_queryset = NewsFeedService.get_cached_newsfeeds(request.user.id)

        page = self.paginator.paginate_cached_list(cached_queryset, request)

        #if 不在cache中， 那我们就去DB里面寻找
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)



        #或者這麽寫
        #queryset = self.paginate_queryset(self.get_queryset())

        serializer = NewsFeedSerializer(
            page,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    # def get_queryset(self):
    #     return NewsFeed.objects.filter(user=self.request.user)