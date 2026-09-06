from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    def __init__(self, method_name: str):
        self._method_name = method_name
        self._is_successful = False
        self._transaction_reference = ""

    @property
    def method_name(self) -> str:
        return self._method_name

    @property
    def is_successful(self) -> bool:
        return self._is_successful

    @property
    def transaction_reference(self) -> str:
        return self._transaction_reference

    @abstractmethod
    def process_payment(self, amount: float) -> tuple[bool, str]:
        pass

    @abstractmethod
    def get_details(self) -> str:
        pass


class CreditCardPayment(PaymentProcessor):
    def __init__(self, card_number: str, card_holder: str, expiry_date: str, cvv: str):
        super().__init__("Credit / Debit Card")
        self._card_number = card_number.replace(" ", "").replace("-", "")
        self._card_holder = card_holder.strip()
        self._expiry_date = expiry_date.strip()
        self._cvv = cvv.strip()

    def process_payment(self, amount: float) -> tuple[bool, str]:
        if amount <= 0:
            return False, "Invalid payment amount"
        if len(self._card_number) != 16 or not self._card_number.isdigit():
            return False, "Invalid card number (must be 16 digits)"
        if len(self._cvv) not in (3, 4) or not self._cvv.isdigit():
            return False, "Invalid CVV code"
        if not self._card_holder:
            return False, "Cardholder name is required"

        self._is_successful = True
        self._transaction_reference = f"CC-{self._card_number[-4:]}-{int(amount * 100)}"
        return True, f"Card payment of ${amount:.2f} processed successfully."

    def get_details(self) -> str:
        masked_num = f"****-****-****-{self._card_number[-4:]}" if len(self._card_number) >= 4 else "Invalid Card"
        return f"{self._method_name} | Holder: {self._card_holder} | Number: {masked_num} | Exp: {self._expiry_date}"


class CashOnDelivery(PaymentProcessor):
    def __init__(self, amount_tendered: float = 0.0):
        super().__init__("Cash on Delivery")
        self._amount_tendered = float(amount_tendered)
        self._change = 0.0

    @property
    def amount_tendered(self) -> float:
        return self._amount_tendered

    @amount_tendered.setter
    def amount_tendered(self, value: float):
        self._amount_tendered = float(value)

    @property
    def change(self) -> float:
        return self._change

    def process_payment(self, amount: float) -> tuple[bool, str]:
        if amount <= 0:
            return False, "Invalid payment amount"
        if self._amount_tendered < amount:
            shortfall = amount - self._amount_tendered
            return False, f"Insufficient cash provided. Short by ${shortfall:.2f}"

        self._change = self._amount_tendered - amount
        self._is_successful = True
        self._transaction_reference = f"COD-{int(amount * 100)}"
        return True, f"Cash payment confirmed. Change: ${self._change:.2f}"

    def get_details(self) -> str:
        return f"{self._method_name} | Cash Given: ${self._amount_tendered:.2f} | Change: ${self._change:.2f}"


class EWalletPayment(PaymentProcessor):
    def __init__(self, provider: str, account_number: str, balance: float = 500.0):
        super().__init__(f"E-Wallet ({provider})")
        self._provider = provider
        self._account_number = account_number.strip()
        self._balance = float(balance)

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def balance(self) -> float:
        return self._balance

    def process_payment(self, amount: float) -> tuple[bool, str]:
        if amount <= 0:
            return False, "Invalid payment amount"
        if not self._account_number:
            return False, "E-Wallet account number is required"
        if self._balance < amount:
            return False, f"Insufficient e-wallet balance (Available: ${self._balance:.2f})"

        self._balance -= amount
        self._is_successful = True
        self._transaction_reference = f"EW-{self._provider[:3].upper()}-{int(amount * 100)}"
        return True, f"E-Wallet payment of ${amount:.2f} successful. Remaining balance: ${self._balance:.2f}"

    def get_details(self) -> str:
        return f"{self._method_name} | Account: {self._account_number} | Available Balance: ${self._balance:.2f}"
