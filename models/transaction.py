from datetime import datetime
from .order import Order
from .payment import PaymentProcessor
from .delivery import Delivery


class Transaction:
    def __init__(
        self,
        transaction_id: str,
        order: Order,
        payment: PaymentProcessor,
        delivery: Delivery,
    ):
        self._transaction_id = transaction_id
        self._order = order
        self._payment = payment
        self._delivery = delivery
        self._timestamp = datetime.now()
        self._total_amount = order.get_total(delivery_fee=delivery.calculate_delivery_fee())

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def order(self) -> Order:
        return self._order

    @property
    def payment(self) -> PaymentProcessor:
        return self._payment

    @property
    def delivery(self) -> Delivery:
        return self._delivery

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def total_amount(self) -> float:
        return self._total_amount

    def get_receipt(self) -> str:
        items_detail = "\n".join(f"    - {item}" for item in self._order.items)
        delivery_fee = self._delivery.calculate_delivery_fee()
        return (
            f"{'=' * 40}\n"
            f"          TRANSACTION RECEIPT\n"
            f"{'=' * 40}\n"
            f"Transaction ID : {self._transaction_id}\n"
            f"Date & Time    : {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Customer       : {self._order.customer.name}\n"
            f"Address        : {self._order.customer.address}\n"
            f"Phone          : {self._order.customer.phone}\n"
            f"{'-' * 40}\n"
            f"Ordered Items:\n{items_detail}\n"
            f"{'-' * 40}\n"
            f"Subtotal       : ${self._order.get_subtotal():.2f}\n"
            f"Tax (5%)       : ${self._order.get_tax():.2f}\n"
            f"Delivery Fee   : ${delivery_fee:.2f} ({self._delivery.get_delivery_type()})\n"
            f"Total Paid     : ${self._total_amount:.2f}\n"
            f"{'-' * 40}\n"
            f"Payment Method : {self._payment.method_name}\n"
            f"Reference      : {self._payment.transaction_reference}\n"
            f"Delivery Status: {self._delivery.status}\n"
            f"Courier        : {self._delivery.agent.name if self._delivery.agent else 'Unassigned'}\n"
            f"{'=' * 40}"
        )


class TransactionHistory:
    def __init__(self):
        self._records: list[Transaction] = []

    def record_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise TypeError("Expected Transaction instance")
        self._records.append(transaction)

    def get_all(self) -> list[Transaction]:
        return list(self._records)

    def find_by_id(self, tx_id: str) -> Transaction | None:
        for tx in self._records:
            if tx.transaction_id == tx_id:
                return tx
        return None

    def get_total_sales(self) -> float:
        return sum(tx.total_amount for tx in self._records)
