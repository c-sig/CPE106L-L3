from abc import ABC, abstractmethod
from .order import Order, OrderStatus


class DeliveryAgent:
    def __init__(self, agent_id: str, name: str, phone: str, vehicle_type: str = "Motorcycle"):
        self._agent_id = agent_id
        self._name = name
        self._phone = phone
        self._vehicle_type = vehicle_type

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def vehicle_type(self) -> str:
        return self._vehicle_type

    def __str__(self) -> str:
        return f"{self._name} ({self._vehicle_type}, Tel: {self._phone})"


class Delivery(ABC):
    def __init__(self, delivery_id: str, order: Order, distance_km: float = 3.0):
        self._delivery_id = delivery_id
        self._order = order
        self._distance_km = max(0.5, float(distance_km))
        self._agent: DeliveryAgent | None = None
        self._status = "Pending Assignment"

    @property
    def delivery_id(self) -> str:
        return self._delivery_id

    @property
    def order(self) -> Order:
        return self._order

    @property
    def distance_km(self) -> float:
        return self._distance_km

    @property
    def agent(self) -> DeliveryAgent | None:
        return self._agent

    @property
    def status(self) -> str:
        return self._status

    def assign_agent(self, agent: DeliveryAgent) -> None:
        self._agent = agent
        self._status = "Agent Assigned"

    def update_status(self, new_status: str) -> None:
        self._status = new_status
        if new_status == "Delivered":
            self._order.status = OrderStatus.DELIVERED
        elif new_status == "Out for Delivery":
            self._order.status = OrderStatus.OUT_FOR_DELIVERY
        elif new_status == "Preparing":
            self._order.status = OrderStatus.PREPARING

    @abstractmethod
    def calculate_delivery_fee(self) -> float:
        pass

    @abstractmethod
    def get_estimated_time_mins(self) -> int:
        pass

    @abstractmethod
    def get_delivery_type(self) -> str:
        pass

    def get_tracking_info(self) -> str:
        agent_info = str(self._agent) if self._agent else "No agent assigned yet"
        return (
            f"Tracking ID: {self._delivery_id}\n"
            f"Type: {self.get_delivery_type()}\n"
            f"Distance: {self._distance_km:.1f} km\n"
            f"Estimated Time: ~{self.get_estimated_time_mins()} mins\n"
            f"Delivery Fee: ${self.calculate_delivery_fee():.2f}\n"
            f"Courier: {agent_info}\n"
            f"Status: {self._status}\n"
            f"Destination: {self._order.customer.address}"
        )


class StandardDelivery(Delivery):
    def get_delivery_type(self) -> str:
        return "Standard Delivery"

    def calculate_delivery_fee(self) -> float:
        return 2.50 + (0.75 * self._distance_km)

    def get_estimated_time_mins(self) -> int:
        return int(30 + (5 * self._distance_km))


class ExpressDelivery(Delivery):
    def get_delivery_type(self) -> str:
        return "Express Delivery"

    def calculate_delivery_fee(self) -> float:
        return 5.00 + (1.25 * self._distance_km)

    def get_estimated_time_mins(self) -> int:
        return int(15 + (3 * self._distance_km))
