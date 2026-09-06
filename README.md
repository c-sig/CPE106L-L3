# Food Delivery System

An Object-Oriented Food Delivery Application developed in Python with a Tkinter Graphical User Interface.

## System Overview

The system models a food delivery platform allowing users to manage customers, browse menu items, create food orders, process payments, track deliveries, and view completed transactions.

### Object-Oriented Design Principles Applied

1. **Encapsulation**:
   - Class state is kept private/protected (e.g. `_customer_id`, `_price`, `_order_id`, `_status`).
   - Access and mutations are handled through validated properties and methods (e.g. non-empty names, non-negative prices, valid quantities).

2. **Inheritance**:
   - `MenuItem` serves as the base class for `FoodItem` (adding cuisine, spice level, vegetarian indicator) and `DrinkItem` (adding size and temperature).
   - `Delivery` serves as the base class for `StandardDelivery` and `ExpressDelivery`.

3. **Abstraction**:
   - `PaymentProcessor` (ABC) defines the abstract interface `process_payment()` and `get_details()`.
   - `Delivery` (ABC) defines abstract methods for `calculate_delivery_fee()`, `get_estimated_time_mins()`, and `get_delivery_type()`.

4. **Polymorphism**:
   - Different payment methods (`CreditCardPayment`, `CashOnDelivery`, `EWalletPayment`) process payments dynamically through the common interface.
   - Different menu item types provide formatted descriptions polymorphically via `get_details()`.
   - Different delivery modes compute fees and estimated delivery times polymorphically.

## Project Structure

```
Lab3/
├── models/
│   ├── __init__.py      # Package exports
│   ├── customer.py      # Customer entity & profile encapsulation
│   ├── menu.py          # MenuItem, FoodItem, DrinkItem, Menu manager
│   ├── order.py         # Order, OrderItem, OrderStatus enum
│   ├── payment.py       # PaymentProcessor, Card, Cash, EWallet
│   ├── delivery.py      # Delivery, StandardDelivery, ExpressDelivery, DeliveryAgent
│   └── transaction.py   # Transaction, TransactionHistory manager
├── app.py               # Tkinter GUI application (4 tabs)
├── main.py              # Entry point with sample data initialization
└── test_system.py       # OOP verification and test script
```

## Running the Application

To run the graphical application:
```bash
python main.py
```

To run the automated verification script:
```bash
python test_system.py
```
