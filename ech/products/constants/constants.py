"""
Product related constants used across the products app.
"""

class ProductType:
    """
    Product type choices used in the Product model.
    """

    PHONE = "PHONE"
    EARPHONE = "EARPHONE"
    HEADSET = "HEADSET"
    MOUSE = "MOUSE"
    KEYBOARD = "KEYBOARD"
    MICROPHONE = "MICROPHONE"

    CHOICES = [
        (PHONE, "Phone"),
        (EARPHONE, "Earphone"),
        (HEADSET, "Headset"),
        (MOUSE, "Mouse"),
        (KEYBOARD, "Keyboard"),
        (MICROPHONE, "Microphone"),
    ]


class ProductImageRules:
    """
    Business rules related to product images.
    """

    MIN_IMAGES_REQUIRED = 3
    MAX_IMAGES_ALLOWED = 10


class ProductInventoryRules:
    """
    Business rules related to inventory control.
    """

    MIN_INVENTORY_ALLOWED = 0


class ProductOrdering:
    """
    Default ordering rules used in selectors.
    """

    NEWEST = "-created_at"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"

