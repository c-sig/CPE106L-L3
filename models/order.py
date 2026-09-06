from datetime import datetime
from enum import Enum
from .customer import Customer
from .menu import MenuItem


class OrderStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    PREPARING = "Preparing"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class OrderItem:
    def __init__(self, item: MenuItem, quantity: int = 1, note: str = ""):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        self._item = item
        self._quantity = quantity
        self._note = note

    @property
    def item(self) -> MenuItem:
        return self._item

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if value <= 0:
            raise ValueError("Quantity must be greater than zero")
        self._quantity = value

    @property
    def note(self) -> str:
        return self._note

    def get_subtotal(self) -> float:
        return self._item.price * self._quantity

    def __str__(self) -> str:
        note_str = f" ({self._note})" if self._note else ""
        return f"{self._item.name} x{self._quantity}{note_str} - ${self.get_subtotal():.2f}"


class Order:
    def __init__(self, order_id: str, customer: Customer):
        if not isinstance(customer, Customer):
            raise TypeError("Expected Customer instance")
        self._order_id = order_id
        self._customer = customer
        self._items: list[OrderItem] = []
        self._status = OrderStatus.PENDING
        self._created_at = datetime.now()

    @property
    def order_id(self) -> str:
        return self._order_id

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, new_status: OrderStatus):
        if not isinstance(new_status, OrderStatus):
            raise TypeError("Status must be an OrderStatus enum member")
        self._status = new_status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def items(self) -> list[OrderItem]:
        return list(self._items)

    def add_item(self, item: MenuItem, quantity: int = 1, note: str = "") -> None:
        for order_item in self._items:
            if order_item.item.item_id == item.item_id and order_item.note == note:
                order_item.quantity += quantity
                return
        self._items.append(OrderItem(item, quantity, note))

    def remove_item(self, item_id: str) -> bool:
        for idx, order_item in enumerate(self._items):
            if order_item.item.item_id == item_id:
                self._items.pop(idx)
                return True
        return False

    def clear_items(self) -> None:
        self._items.clear()

    def get_subtotal(self) -> float:
        return sum(item.get_subtotal() for item in self._items)

    def get_tax(self, rate: float = 0.05) -> float:
        return self.get_subtotal() * rate

    def get_total(self, delivery_fee: float = 0.0, tax_rate: float = 0.05) -> float:
        return self.get_subtotal() + self.get_tax(tax_rate) + delivery_fee

    def get_summary(self, delivery_fee: float = 0.0) -> str:
        lines = [
            f"Order ID: {self._order_id}",
            f"Customer: {self._customer.name} ({self._customer.phone})",
            f"Address: {self._customer.address}",
            f"Date: {self._created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Status: {self._status.value}",
            "-" * 30,
            "Items:",
        ]
        for item in self._items:
            lines.append(f"  - {item}")
        lines.append("-" * 30)
        lines.append(f"Subtotal: ${self.get_subtotal():.2f}")
        lines.append(f"Tax (5%): ${self.get_tax():.2f}")
        if delivery_fee > 0:
            lines.append(f"Delivery Fee: ${delivery_fee:.2f}")
        lines.append(f"Total: ${self.get_total(delivery_fee):.2f}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Order #{self._order_id} - {self._customer.name} (${self.get_subtotal():.2f})"
