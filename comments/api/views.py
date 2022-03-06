from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.decorators import required_params

# Create your views here.
class CommentViewSet(viewsets.GenericViewSet):
    #django的ui界面里面测试的时候 基于哪个界面去进行渲染
    serializer_class = CommentSerializerForCreate
    #可加可不加，反正后面会重写，
    # 但get_object会基于queryset
    #但用上了filter_backend就不可以不加了
    #因为要get_queryset
    queryset = Comment.objects.all()

    #指定那些可以自动变成filter的选项,
    # 甚至还有很多更灵活的搜索方式
    filterset_fields = ('tweet_id',)


    def get_permissions(self):
        # 注意要加用 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是 AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        # serializer = CommentSerializer(comments, many=True)
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(
            comments,
            many=True,
            context={'request': request},
        )
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        #第一步知道data
        #也可以是把request作为context传进serializers中，去读取user_id，
        # 这样直接读取
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        #因为第一个默认是instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        #save 会 call serializer中create
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            #一定要传进去这个instance，DRF中有get_object会自动检查
            instance = comment,
            data = request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input'
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
            # 渲染结果
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()

        return Response({
            'success': True
        }, status=status.HTTP_200_OK)




