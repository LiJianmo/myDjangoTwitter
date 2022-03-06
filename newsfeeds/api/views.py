from django.shortcuts import render
from rest_framework import viewsets, status
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        #NewsFeedSerializer需要的参数就是一个有关newsfeed的queryset
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            many=True,
            context={'request': request},
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)