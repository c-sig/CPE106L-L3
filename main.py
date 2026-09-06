from models.customer import Customer
from models.menu import Menu, FoodItem, DrinkItem
from models.delivery import DeliveryAgent
from app import FoodDeliveryApp


def initialize_sample_data():
    customers = [
        Customer("C001", "Alice Smith", "555-0101", "123 Maple Street"),
        Customer("C002", "Bob Johnson", "555-0202", "456 Oak Avenue"),
        Customer("C003", "Charlie Davis", "555-0303", "789 Pine Road"),
    ]

    menu = Menu()
    # Food items
    menu.add_item(FoodItem("F101", "Classic Cheeseburger", 9.99, "American", "Mild", False))
    menu.add_item(FoodItem("F102", "Spicy Chicken Burger", 10.50, "American", "Spicy", False))
    menu.add_item(FoodItem("F103", "Margherita Pizza", 12.99, "Italian", "None", True))
    menu.add_item(FoodItem("F104", "Pepperoni Feast Pizza", 14.50, "Italian", "Mild", False))
    menu.add_item(FoodItem("F105", "Crispy French Fries", 4.25, "Sides", "None", True))
    menu.add_item(FoodItem("F106", "Caesar Salad", 7.50, "Salad", "None", True))

    # Drink items
    menu.add_item(DrinkItem("D201", "Iced Lemon Tea", 3.50, "Large", True))
    menu.add_item(DrinkItem("D202", "Fresh Berry Smoothie", 5.00, "Regular", True))
    menu.add_item(DrinkItem("D203", "Hot Cappuccino", 4.50, "Regular", False))
    menu.add_item(DrinkItem("D204", "Sparkling Water", 2.50, "Regular", True))

    agents = [
        DeliveryAgent("A01", "David Rider", "555-9111", "Motorcycle"),
        DeliveryAgent("A02", "Emma Swift", "555-9222", "Bicycle"),
        DeliveryAgent("A03", "Frank Wheeler", "555-9333", "Car"),
    ]

    return menu, customers, agents


def main():
    menu, customers, agents = initialize_sample_data()
    app = FoodDeliveryApp(menu, customers, agents)
    app.mainloop()


if __name__ == "__main__":
    main()
