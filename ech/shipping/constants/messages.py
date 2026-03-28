# =============================
# SHIPMENT CREATION
# =============================

SHIPMENT_ALREADY_EXISTS = "A shipment already exists for this order."
SHIPMENT_CREATION_SUCCESS = "Shipment successfully created."
SHIPMENT_CREATION_FAILED = "Shipment creation failed."

# =============================
# SHIPMENT RETRIEVAL
# =============================

SHIPMENT_NOT_FOUND = "Shipment not found."
SHIPMENT_ACCESS_DENIED = "You do not have permission to access this shipment."

# =============================
# SHIPMENT UPDATE
# =============================

SHIPMENT_UPDATE_SUCCESS = "Shipment updated successfully."
SHIPMENT_UPDATE_FAILED = "Shipment update failed."
SHIPMENT_UPDATE_NOT_ALLOWED = "Shipment update is not allowed in the current status."

# =============================
# SHIPMENT STATUS MANAGEMENT
# =============================

INVALID_SHIPMENT_STATUS_TRANSITION = "Invalid shipment status transition."
SHIPMENT_STATUS_UPDATED = "Shipment status updated successfully."
SHIPMENT_ALREADY_DELIVERED = "Shipment has already been delivered."
SHIPMENT_ALREADY_CANCELLED = "Shipment has already been cancelled."
SHIPMENT_CANNOT_BE_MODIFIED = "Shipment cannot be modified in its current state."

# =============================
# SHIPMENT PROCESSING
# =============================

SHIPMENT_PROCESSING_STARTED = "Shipment processing started."
SHIPMENT_PROCESSING_FAILED = "Shipment processing failed."

# =============================
# SHIPMENT CANCELLATION
# =============================

SHIPMENT_CANCELLED_SUCCESS = "Shipment cancelled successfully."
SHIPMENT_CANCELLATION_NOT_ALLOWED = "Shipment cannot be cancelled in its current state."

# =============================
# SHIPMENT MANAGEMENT
# =============================

TRACKING_CODE_REQUIRED = "Tracking code is required."
TRACKING_UPDATE_SUCCESS = "Tracking information updated successfully."
TRACKING_UPDATE_FAILED = "Tracking update failed."
INVALID_TRACKING_EVENT = "Invalid tracking update event."

# =============================
# SHIPMENT DELIVERY
# =============================

SHIPMENT_MARKED_AS_DELIVERED = "Shipment marked as delivered."
DELIVERY_CONFIRMATION_REQUIRED = "Delivery confirmation information is required."

# =============================
# ADDRESS MANAGEMENT
# =============================

INVALID_SHIPPING_ADDRESS = "Invalid shipping address."
ADDRESS_UPDATE_NOT_ALLOWED = "Shipping address cannot be updated after shipment processing has started."

# =============================
# SHIPMENT OPERATIONAL NOTES
# =============================

SHIPMENT_NOTE_HELP_TEXT = "Internal notes are only visible to operational staff."

# =============================
# SHIPMENT LOGGING
# =============================

LOG_SHIPMENT_CREATED = "Shipment created."
LOG_SHIPMENT_UPDATED = "Shipment updated."
LOG_SHIPMENT_STATUS_CHANGED = "Shipment status changed."
LOG_SHIPMENT_CANCELLED = "Shipment cancelled."
LOG_TRACKING_UPDATED = "Shipment tracking updated."


# =============================
# SHIPMENT IDEMPOTENCY
# =============================

IDEMPOTENCY_KEY_CONFLICT = "This idempotency key has already been used for a different shipment request."