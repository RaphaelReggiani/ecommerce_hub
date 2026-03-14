from rest_framework.pagination import PageNumberPagination


class OrderPagination(PageNumberPagination):
    """
    Default pagination for order list endpoints.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
