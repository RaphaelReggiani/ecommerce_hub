from rest_framework.pagination import PageNumberPagination


class PaymentPagination(PageNumberPagination):
    """
    Default pagination class for payment list endpoints.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100