from django.shortcuts import render
from rest_framework import viewsets, status
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination

# Create your views here.
class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    pagination_class = EndlessPagination

    def list(self, request):
        #NewsFeedSerializer需要的参数就是一个有关newsfeed的queryset
        query = NewsFeed.objects.filter(user=self.request.user)
        page = self.paginate_queryset(query)

        #或者這麽寫
        #queryset = self.paginate_queryset(self.get_queryset())

        serializer = NewsFeedSerializer(
            page,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)