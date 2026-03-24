from ech.shipping.domain_events.events import (
    ShipmentCreatedEvent,
    ShipmentStatusChangedEvent,
)
from ech.shipping.domain_events.handlers import (
    handle_shipment_created,
    handle_shipment_status_changed,
)


EVENT_HANDLER_REGISTRY = {
    ShipmentCreatedEvent: [
        handle_shipment_created,
    ],
    ShipmentStatusChangedEvent: [
        handle_shipment_status_changed,
    ],
}