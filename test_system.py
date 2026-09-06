from models.customer import Customer
from models.menu import Menu, FoodItem, DrinkItem
from models.order import Order, OrderStatus
from models.payment import CreditCardPayment, CashOnDelivery, EWalletPayment
from models.delivery import StandardDelivery, ExpressDelivery, DeliveryAgent
from models.transaction import Transaction, TransactionHistory


def test_oop_principles():
    print("=== Testing Object-Oriented Design Principles ===")

    # 1. Encapsulation Test
    cust = Customer("C001", "Alice Smith", "555-0199", "123 Maple St")
    assert cust.name == "Alice Smith"
    try:
        cust.name = ""
        assert False, "Should raise ValueError on empty name"
    except ValueError:
        pass
    print("[PASS] Encapsulation: Customer validation and properties work.")

    # 2. Inheritance & Polymorphism Test (Menu items)
    menu = Menu()
    burger = FoodItem("F01", "Cheeseburger", 8.99, "American", "Mild", False)
    salad = FoodItem("F02", "Garden Salad", 6.50, "Fresh", "None", True)
    tea = DrinkItem("D01", "Iced Green Tea", 3.25, "Large", True)
    coffee = DrinkItem("D02", "Hot Latte", 4.00, "Regular", False)

    menu.add_item(burger)
    menu.add_item(salad)
    menu.add_item(tea)
    menu.add_item(coffee)

    for item in menu.get_all_items():
        details = item.get_details()
        assert len(details) > 0
        print(f"  - {item.category} Polymorphic details: {details}")
    print("[PASS] Inheritance & Polymorphism: MenuItem subclasses format details polymorphically.")

    # 3. Order Management Test
    order = Order("ORD-1001", cust)
    order.add_item(burger, 2, "No onions")
    order.add_item(tea, 1)
    subtotal = (8.99 * 2) + 3.25
    assert abs(order.get_subtotal() - subtotal) < 0.01
    print(f"[PASS] Order: Subtotal calculated correctly (${order.get_subtotal():.2f}).")

    # 4. Abstraction & Polymorphism Test (Delivery)
    agent = DeliveryAgent("A01", "Dave Rider", "555-8888", "Scooter")
    standard_del = StandardDelivery("DEL-S1", order, distance_km=4.0)
    standard_del.assign_agent(agent)
    express_del = ExpressDelivery("DEL-E1", order, distance_km=4.0)
    express_del.assign_agent(agent)

    std_fee = standard_del.calculate_delivery_fee()
    exp_fee = express_del.calculate_delivery_fee()
    assert exp_fee > std_fee
    print(f"[PASS] Delivery Abstraction: Standard (${std_fee:.2f}) vs Express (${exp_fee:.2f}).")

    # 5. Abstraction & Polymorphism Test (Payments)
    card_pay = CreditCardPayment("4111111111111234", "Alice Smith", "12/28", "123")
    total = order.get_total(delivery_fee=exp_fee)
    ok, msg = card_pay.process_payment(total)
    assert ok is True
    print(f"[PASS] Payment Polymorphism (Card): {msg}")

    # Test cash on delivery insufficient
    cash_pay = CashOnDelivery(amount_tendered=10.0)
    ok_cash, msg_cash = cash_pay.process_payment(total)
    assert ok_cash is False
    print(f"[PASS] Payment Validation (Cash): Correctly declined insufficient funds ({msg_cash}).")

    # Test cash sufficient
    cash_pay.amount_tendered = 50.0
    ok_cash, msg_cash = cash_pay.process_payment(total)
    assert ok_cash is True

    # 6. Transaction Recording Test
    history = TransactionHistory()
    tx = Transaction("TXN-001", order, card_pay, express_del)
    history.record_transaction(tx)
    assert len(history.get_all()) == 1
    assert history.get_total_sales() > 0
    print(f"[PASS] Transaction: Recorded successfully. Total sales = ${history.get_total_sales():.2f}")
    print("\nAll OOP tests completed successfully!")


if __name__ == "__main__":
    test_oop_principles()
