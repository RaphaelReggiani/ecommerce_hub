from rest_framework.pagination import PageNumberPagination


class NotificationsPagination(PageNumberPagination):
    """
    Default pagination for notifications list endpoints.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
