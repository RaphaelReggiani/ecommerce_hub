from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, 
    ListAPIView, 
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from ech.orders.filters import OrderFilter
from ech.orders.selectors import (
    get_order_detail_for_management,
    list_orders_for_management,
)
from ech.orders.services.order_status_service import OrderStatusService
from ech.orders.api.permissions import CanManageOrders
from ech.orders.api.serializers import (
    OrderManagementListSerializer,
    OrderManagementDetailSerializer,
)

from rest_framework.exceptions import NotFound

from ech.orders.exceptions import OrderError

from ech.orders.api.permissions import (
    IsOrderOwner,
    IsOrderOwnerOrCanManageOrders,
)

from ech.orders.api.pagination import (
    OrderPagination,
)

from ech.orders.api.serializers import (
    CreateOrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)
from ech.orders.selectors import (
    get_order_by_id,
    list_orders_by_customer,
)
from ech.orders.services.cancel_order_service import (
    CancelOrderService,
)

from ech.orders.constants.messages import (
    MSG_ERROR_ORDER_NOT_FOUND,
)


class OrderCreateAPIView(CreateAPIView):
    """
    API endpoint for creating a new order.
    """

    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            order = serializer.save()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = OrderDetailSerializer(
            order,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderListAPIView(ListAPIView):
    """
    API endpoint for listing orders of the authenticated customer.
    """

    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        return list_orders_by_customer(self.request.user)


class OrderDetailAPIView(RetrieveAPIView):
    """
    API endpoint for retrieving a specific order detail.

    Customers can access their own orders.
    Staff with order management roles can also access the order.
    """

    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrCanManageOrders]
    lookup_url_kwarg = "order_id"

    def get_object(self):
        order_id = self.kwargs.get(self.lookup_url_kwarg)
        order = get_order_by_id(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        self.check_object_permissions(self.request, order)

        return order


class OrderCancelAPIView(APIView):
    """
    API endpoint for cancelling an order.

    Customers can only cancel their own orders.
    """

    permission_classes = [IsAuthenticated, IsOrderOwner]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_by_id(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        self.check_object_permissions(request, order)

        service = CancelOrderService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.execute()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_by_id(order.id)
        serializer = OrderDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderManagementListAPIView(ListAPIView):
    """
    API endpoint for staff management order listing.
    """

    serializer_class = OrderManagementListSerializer
    permission_classes = [IsAuthenticated, CanManageOrders]
    pagination_class = OrderPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_queryset(self):
        return list_orders_for_management()


class OrderManagementDetailAPIView(RetrieveAPIView):
    """
    API endpoint for staff management order detail.
    """

    serializer_class = OrderManagementDetailSerializer
    permission_classes = [IsAuthenticated, CanManageOrders]
    lookup_url_kwarg = "order_id"

    def get_object(self):
        order_id = self.kwargs.get(self.lookup_url_kwarg)
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        return order


class OrderConfirmAPIView(APIView):
    """
    API endpoint for confirming an order in staff management flow.
    """

    permission_classes = [IsAuthenticated, CanManageOrders]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        service = OrderStatusService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.confirm_order()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_detail_for_management(order.id)
        serializer = OrderManagementDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderStartProcessingAPIView(APIView):
    """
    API endpoint for starting order processing in staff management flow.
    """

    permission_classes = [IsAuthenticated, CanManageOrders]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        service = OrderStatusService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.start_processing()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_detail_for_management(order.id)
        serializer = OrderManagementDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderShipAPIView(APIView):
    """
    API endpoint for shipping an order in staff management flow.
    """

    permission_classes = [IsAuthenticated, CanManageOrders]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        service = OrderStatusService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.ship_order()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_detail_for_management(order.id)
        serializer = OrderManagementDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderDeliverAPIView(APIView):
    """
    API endpoint for delivering an order in staff management flow.
    """

    permission_classes = [IsAuthenticated, CanManageOrders]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        service = OrderStatusService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.deliver_order()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_detail_for_management(order.id)
        serializer = OrderManagementDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderManagementCancelAPIView(APIView):
    """
    API endpoint for cancelling an order in staff management flow.
    """

    permission_classes = [IsAuthenticated, CanManageOrders]

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_detail_for_management(order_id)

        if not order:
            raise NotFound(MSG_ERROR_ORDER_NOT_FOUND)

        service = CancelOrderService(
            order=order,
            performed_by=request.user,
        )

        try:
            service.execute()
        except OrderError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_order = get_order_detail_for_management(order.id)
        serializer = OrderManagementDetailSerializer(updated_order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
