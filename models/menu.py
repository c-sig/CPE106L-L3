from abc import ABC, abstractmethod


class MenuItem(ABC):
    def __init__(self, item_id: str, name: str, price: float, category: str):
        self._item_id = item_id
        self._name = name
        self._category = category
        self.price = price

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Item name cannot be empty")
        self._name = value.strip()

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = float(value)

    @property
    def category(self) -> str:
        return self._category

    @abstractmethod
    def get_details(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self._name} - ${self._price:.2f}"


class FoodItem(MenuItem):
    def __init__(
        self,
        item_id: str,
        name: str,
        price: float,
        cuisine: str,
        spice_level: str = "Mild",
        is_vegetarian: bool = False,
    ):
        super().__init__(item_id, name, price, category="Food")
        self._cuisine = cuisine
        self._spice_level = spice_level
        self._is_vegetarian = is_vegetarian

    @property
    def cuisine(self) -> str:
        return self._cuisine

    @property
    def spice_level(self) -> str:
        return self._spice_level

    @property
    def is_vegetarian(self) -> bool:
        return self._is_vegetarian

    def get_details(self) -> str:
        veg_tag = "Veg" if self._is_vegetarian else "Non-Veg"
        return f"{self._name} (${self._price:.2f}) [{self._cuisine}, {veg_tag}, Spice: {self._spice_level}]"


class DrinkItem(MenuItem):
    def __init__(
        self,
        item_id: str,
        name: str,
        price: float,
        size: str = "Regular",
        is_cold: bool = True,
    ):
        super().__init__(item_id, name, price, category="Drink")
        self._size = size
        self._is_cold = is_cold

    @property
    def size(self) -> str:
        return self._size

    @property
    def is_cold(self) -> bool:
        return self._is_cold

    def get_details(self) -> str:
        temp_tag = "Iced" if self._is_cold else "Hot"
        return f"{self._name} (${self._price:.2f}) [Size: {self._size}, {temp_tag}]"


class Menu:
    def __init__(self):
        self._items: dict[str, MenuItem] = {}

    def add_item(self, item: MenuItem) -> None:
        if not isinstance(item, MenuItem):
            raise TypeError("Expected a MenuItem instance")
        self._items[item.item_id] = item

    def remove_item(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def get_item(self, item_id: str) -> MenuItem | None:
        return self._items.get(item_id)

    def get_all_items(self) -> list[MenuItem]:
        return list(self._items.values())

    def get_items_by_category(self, category: str) -> list[MenuItem]:
        return [item for item in self._items.values() if item.category.lower() == category.lower()]
