class BaseDomainEvent:
    """
    Base domain event.
    """

    event_name = "base_domain_event"

    def to_dict(self):
        """
        Serialize event payload for logging, debugging, or handlers.
        """

        return self.__dict__.copy()


class ShipmentCreatedEvent(BaseDomainEvent):
    """
    Event triggered when a shipment is created.
    """

    event_name = "shipment_created"

    def __init__(
        self,
        *,
        shipment_id,
        order_id,
        customer_id,
        performed_by_id=None,
    ):
        self.shipment_id = shipment_id
        self.order_id = order_id
        self.customer_id = customer_id
        self.performed_by_id = performed_by_id


class ShipmentStatusChangedEvent(BaseDomainEvent):
    """
    Event triggered when a shipment status changes.
    """

    event_name = "shipment_status_changed"

    def __init__(
        self,
        *,
        shipment_id,
        previous_status,
        new_status,
        performed_by_id=None,
    ):
        self.shipment_id = shipment_id
        self.previous_status = previous_status
        self.new_status = new_status
        self.performed_by_id = performed_by_id