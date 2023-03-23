from django.utils.translation import gettext_lazy as _
from typing import Any, List
from salesman.orders.status import BaseOrderStatus


class OrderStatus(BaseOrderStatus):
    """
    Custom order status choices for a point of sale (POS) syste
    in a restaurant. Required choices are NEW, CREATED,
    COMPLETED and REFUNDED.
    """

    NEW = "NEW", _("New")  # Order with reference created, items are in the basket.
    CREATED = "CREATED", _("Created")  # Created with items and pending payment.

    HOLD = "HOLD", _("Hold")  # Stock reduced but still awaiting payment.
    FAILED = "FAILED", _("Failed")  # Payment failed, retry is available.
    CANCELLED = "CANCELLED", _("Cancelled")  # Cancelled by seller, stock increased.

    PROCESSING = "PROCESSING", _("Processing")  # Payment confirmed, processing order.
    SHIPPED = "SHIPPED", _("Shipped")  # Shipped to customer.
    
    POS_PREPARING = "POS_PREPARING", _("In Progress")  # Order in production (preparing coffee, sandwich, etc.).
    POS_READY = "POS_READY", _("Ready")  # Order ready to be delivered/served to the customer.
    POS_REMAKE = "POS_REMAKE", _("Remake")  # Order damaged or lost before being served to the customer.
    POS_SERVED = "POS_SERVED", _("Served")  # Order delivered/served to the customer.
    POS_PAID = "POS_PAID", _("Paid")  # Order paid by the customer.

    COMPLETED = "COMPLETED", _("Completed")  # Completed and received by customer.
    REFUNDED = "REFUNDED", _("Refunded")  # Fully refunded by seller.

    @classmethod
    def get_payable(cls) -> list[Any]:
        """
        Returns default payable statuses.
        """
        return [cls.CREATED, cls.HOLD, cls.FAILED]

    @classmethod
    def get_transitions(cls) -> dict[str, list[Any]]:
        """
        Returns default status transitions.
        """
        #TODO: Add transitions for POS_PREPARING, POS_READY, POS_REMAKE, POS_SERVED, POS_PAID
        return {
            "NEW": [cls.CREATED],
            "CREATED": [cls.HOLD, cls.FAILED, cls.CANCELLED, cls.PROCESSING, cls.POS_PREPARING, cls.POS_READY, cls.POS_REMAKE],
            "HOLD": [cls.FAILED, cls.CANCELLED, cls.PROCESSING],
            "FAILED": [cls.CANCELLED, cls.PROCESSING],
            "CANCELLED": [],
            "PROCESSING": [cls.SHIPPED, cls.COMPLETED, cls.REFUNDED],
            "SHIPPED": [cls.COMPLETED, cls.REFUNDED],
            "COMPLETED": [cls.REFUNDED],
            "REFUNDED": [],
        }