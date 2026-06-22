import random
from datetime import datetime, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from app.models.tables import Customer, Order, Refund


fake = Faker()


CUSTOMER_COUNT = 100_000
ORDER_COUNT = 1_000_000
REFUND_COUNT = 200_000

BATCH_SIZE = 10_000


def clear_existing_data(db: Session):
    db.query(Refund).delete()
    db.query(Order).delete()
    db.query(Customer).delete()
    db.commit()


def generate_customers(db: Session, seed: int):
    random.seed(seed)
    Faker.seed(seed)

    countries = ["India", "USA", "UK", "Canada", "Germany", "Australia", "UAE"]

    customers = []

    for i in range(1, CUSTOMER_COUNT + 1):
        customers.append(
            {
                "id": i,
                "name": fake.name(),
                "email": f"user{i}@example.com",
                "country": random.choice(countries),
                "created_at": fake.date_time_between(
                    start_date="-3y",
                    end_date="now",
                ),
            }
        )

        if len(customers) >= BATCH_SIZE:
            db.bulk_insert_mappings(Customer, customers)
            db.commit()
            customers.clear()
            print(f"Inserted customers up to {i}")

    if customers:
        db.bulk_insert_mappings(Customer, customers)
        db.commit()

    print("Customers generated successfully")


def generate_orders(db: Session, seed: int):
    random.seed(seed + 1)

    statuses = ["completed", "completed", "completed", "completed", "cancelled"]

    orders = []
    start_date = datetime.now() - timedelta(days=730)

    for i in range(1, ORDER_COUNT + 1):
        amount = round(random.uniform(100, 20_000), 2)

        orders.append(
            {
                "id": i,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "amount": Decimal(str(amount)),
                "status": random.choice(statuses),
                "created_at": start_date + timedelta(
                    days=random.randint(0, 730),
                    seconds=random.randint(0, 86_400),
                ),
            }
        )

        if len(orders) >= BATCH_SIZE:
            db.bulk_insert_mappings(Order, orders)
            db.commit()
            orders.clear()
            print(f"Inserted orders up to {i}")

    if orders:
        db.bulk_insert_mappings(Order, orders)
        db.commit()

    print("Orders generated successfully")


def generate_refunds(db: Session, seed: int):
    random.seed(seed + 2)

    reasons = [
        "Damaged product",
        "Late delivery",
        "Customer changed mind",
        "Duplicate order",
        "Payment issue",
    ]

    refunds = []

    for i in range(1, REFUND_COUNT + 1):
        order_id = random.randint(1, ORDER_COUNT)
        customer_id = random.randint(1, CUSTOMER_COUNT)
        amount = round(random.uniform(20, 5_000), 2)

        refunds.append(
            {
                "id": i,
                "order_id": order_id,
                "customer_id": customer_id,
                "amount": Decimal(str(amount)),
                "reason": random.choice(reasons),
                "created_at": datetime.now() - timedelta(
                    days=random.randint(0, 730)
                ),
            }
        )

        if len(refunds) >= BATCH_SIZE:
            db.bulk_insert_mappings(Refund, refunds)
            db.commit()
            refunds.clear()
            print(f"Inserted refunds up to {i}")

    if refunds:
        db.bulk_insert_mappings(Refund, refunds)
        db.commit()

    print("Refunds generated successfully")


def generate_all_data(db: Session, seed: int = 42):
    print("Clearing old data...")
    clear_existing_data(db)

    print("Generating customers...")
    generate_customers(db, seed)

    print("Generating orders...")
    generate_orders(db, seed)

    print("Generating refunds...")
    generate_refunds(db, seed)

    print("All data generated successfully")