from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend

from ech.shipping.constants.messages import (
    SHIPMENT_NOT_FOUND,
)
from ech.shipping.exceptions import (
    ShippingException,
    ShipmentNotFoundException,
)
from ech.shipping.selectors import (
    get_shipment_by_id,
    list_customer_shipments,
    list_management_shipments,
)
from ech.shipping.filters import (
    ShipmentFilter,
    ShipmentManagementFilter,
)
from ech.shipping.api.permissions import (
    CanManageShipments,
    IsShipmentOwnerOrCanManageShipments,
)
from ech.shipping.api.pagination import ShippingPagination
from ech.shipping.api.serializers import (
    CreateShipmentSerializer,
    ShipmentListSerializer,
    ShipmentDetailSerializer,
    ShipmentUpdateSerializer,
    ShipmentProcessSerializer,
    ShipmentCancelSerializer,
    ShipmentTrackingSerializer,
    ShipmentManagementListSerializer,
    ShipmentManagementDetailSerializer,
)


class ShipmentCreateAPIView(CreateAPIView):
    """
    API endpoint for creating a new shipment.

    Restricted to staff roles allowed to manage shipping.
    """

    serializer_class = CreateShipmentSerializer
    permission_classes = [IsAuthenticated, CanManageShipments]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            shipment = serializer.save()
        except ShippingException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ShipmentManagementDetailSerializer(
            shipment,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ShipmentListAPIView(ListAPIView):
    """
    API endpoint for listing shipments of the authenticated customer.
    """

    serializer_class = ShipmentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ShippingPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ShipmentFilter

    def get_queryset(self):
        return list_customer_shipments(customer=self.request.user)


class ShipmentDetailAPIView(RetrieveAPIView):
    """
    API endpoint for retrieving a specific shipment detail.
    """

    serializer_class = ShipmentDetailSerializer
    permission_classes = [IsAuthenticated, IsShipmentOwnerOrCanManageShipments]
    lookup_url_kwarg = "shipment_id"

    def get_object(self):
        shipment_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        self.check_object_permissions(self.request, shipment)
        return shipment


class ShipmentUpdateAPIView(APIView):
    """
    API endpoint for updating shipment operational data and/or address snapshot.
    """

    permission_classes = [IsAuthenticated, CanManageShipments]

    def patch(self, request, shipment_id, *args, **kwargs):
        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        serializer = ShipmentUpdateSerializer(
            data=request.data,
            context={
                "request": request,
                "shipment": shipment,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_shipment = serializer.save(
                shipment=shipment,
                performed_by=request.user,
            )
        except ShippingException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ShipmentManagementDetailSerializer(
            updated_shipment,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ShipmentProcessAPIView(APIView):
    """
    API endpoint for performing a controlled shipment status transition.
    """

    permission_classes = [IsAuthenticated, CanManageShipments]

    def post(self, request, shipment_id, *args, **kwargs):
        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        serializer = ShipmentProcessSerializer(
            data=request.data,
            context={
                "request": request,
                "shipment": shipment,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_shipment = serializer.save(
                shipment=shipment,
                performed_by=request.user,
            )
        except ShippingException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ShipmentManagementDetailSerializer(
            updated_shipment,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ShipmentCancelAPIView(APIView):
    """
    API endpoint for cancelling a shipment.
    """

    permission_classes = [IsAuthenticated, CanManageShipments]

    def post(self, request, shipment_id, *args, **kwargs):
        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        serializer = ShipmentCancelSerializer(
            data=request.data,
            context={
                "request": request,
                "shipment": shipment,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_shipment = serializer.save(
                shipment=shipment,
                performed_by=request.user,
            )
        except ShippingException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ShipmentManagementDetailSerializer(
            updated_shipment,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ShipmentTrackingAPIView(APIView):
    """
    API endpoint for registering a shipment tracking update.
    """

    permission_classes = [IsAuthenticated, CanManageShipments]

    def post(self, request, shipment_id, *args, **kwargs):
        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        serializer = ShipmentTrackingSerializer(
            data=request.data,
            context={
                "request": request,
                "shipment": shipment,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save(
                shipment=shipment,
                performed_by=request.user,
            )
        except ShippingException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_shipment = get_shipment_by_id(shipment_id=shipment.id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        output_serializer = ShipmentManagementDetailSerializer(
            updated_shipment,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ShipmentManagementListAPIView(ListAPIView):
    """
    API endpoint for staff management shipment listing.
    """

    serializer_class = ShipmentManagementListSerializer
    permission_classes = [IsAuthenticated, CanManageShipments]
    pagination_class = ShippingPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ShipmentManagementFilter

    def get_queryset(self):
        return list_management_shipments()


class ShipmentManagementDetailAPIView(RetrieveAPIView):
    """
    API endpoint for staff shipment management detail.
    """

    serializer_class = ShipmentManagementDetailSerializer
    permission_classes = [IsAuthenticated, CanManageShipments]
    lookup_url_kwarg = "shipment_id"

    def get_object(self):
        shipment_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            shipment = get_shipment_by_id(shipment_id=shipment_id)
        except ShipmentNotFoundException:
            raise NotFound(SHIPMENT_NOT_FOUND)

        return shipment