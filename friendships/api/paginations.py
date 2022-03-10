from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FriendshipPagination(PageNumberPagination):

    #when page number not in url, we have a initial page number
    page_size = 20
    #when param = None, means that client cannot specify the page size
    #now, client can use size=??? to specify the size
    #specify size in url
    #page_query_param 用來決定page
    # Client can control the page using this query parameter.
    #page_query_param = 'page'


    page_size_query_param = 'size'
    # maximum size can align
    max_page_size = 20

    #https://.../api/friendships/1/followrs/?page=3&size=10

    #return the data got to front end and package them
    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })

