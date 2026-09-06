class Customer:
    def __init__(self, customer_id: str, name: str, phone: str, address: str):
        self._customer_id = customer_id
        self._name = name
        self._phone = phone
        self._address = address

    @property
    def customer_id(self) -> str:
        return self._customer_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Customer name cannot be empty")
        self._name = value.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if not value.strip():
            raise ValueError("Phone number cannot be empty")
        self._phone = value.strip()

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        if not value.strip():
            raise ValueError("Address cannot be empty")
        self._address = value.strip()

    def get_info(self) -> str:
        return f"[{self._customer_id}] {self._name} | Phone: {self._phone} | Address: {self._address}"

    def __str__(self) -> str:
        return f"{self._name} ({self._customer_id})"
