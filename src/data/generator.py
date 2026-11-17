"""Synthetic transaction generator for testing and demonstration."""
import random
import uuid
from datetime import date, timedelta
from src.data.schema import Transaction, TransactionType


def generate_mock_transactions(days: int = 180, seed: int = 42) -> list[Transaction]:
    """Generates a realistic sequence of transactions over the past `days`."""
    random.seed(seed)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    transactions: list[Transaction] = []

    # Accounts
    accounts = ["Main Checking", "Credit Card", "High-Yield Savings", "Cash Wallet"]

    # Category profiles: (category, min_amount, max_amount, default_account, frequency_per_month)
    expense_profiles = [
        ("Housing", 1200.0, 1200.0, "Main Checking", "monthly"),       # Rent/Mortgage
        ("Utilities", 120.0, 220.0, "Main Checking", "monthly"),
        ("Subscriptions", 12.99, 45.0, "Credit Card", "monthly"),
        ("Groceries", 35.0, 150.0, "Credit Card", "weekly_multiple"),
        ("Dining Out", 15.0, 80.0, "Credit Card", "weekly_multiple"),
        ("Transportation", 20.0, 65.0, "Credit Card", "weekly"),
        ("Entertainment", 25.0, 120.0, "Credit Card", "biweekly"),
        ("Shopping", 30.0, 250.0, "Credit Card", "biweekly"),
        ("Healthcare", 40.0, 180.0, "Credit Card", "monthly_sparse"),
    ]

    curr_date = start_date
    while curr_date <= end_date:
        day_of_month = curr_date.day

        # 1. Bi-weekly Salary (1st and 15th)
        if day_of_month in (1, 15):
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=2850.00,
                    type=TransactionType.INCOME,
                    category="Salary",
                    account="Main Checking",
                    note="Bi-weekly Paycheck",
                    tags=["income", "payroll"]
                )
            )

        # 2. Monthly Freelance Gig / Dividend
        if day_of_month == 20 and random.random() > 0.3:
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(300.0, 950.0), 2),
                    type=TransactionType.INCOME,
                    category="Freelance",
                    account="Main Checking",
                    note="Side Project Consulting",
                    tags=["income", "freelance"]
                )
            )

        # 3. Monthly Fixed Expenses
        if day_of_month == 1:
            # Rent
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=1200.00,
                    type=TransactionType.EXPENSE,
                    category="Housing",
                    account="Main Checking",
                    note="Monthly Apartment Rent",
                    tags=["fixed", "essential"]
                )
            )
        if day_of_month == 5:
            # Utilities
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(110.0, 180.0), 2),
                    type=TransactionType.EXPENSE,
                    category="Utilities",
                    account="Main Checking",
                    note="Electricity & Water",
                    tags=["bills"]
                )
            )
        if day_of_month == 10:
            # Subscriptions
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=29.98,
                    type=TransactionType.EXPENSE,
                    category="Subscriptions",
                    account="Credit Card",
                    note="Streaming & Cloud Storage",
                    tags=["recurring"]
                )
            )

        # 4. Variable daily/weekly expenses
        # Groceries: 2-3 times a week
        if random.random() < 0.4:
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(35.0, 140.0), 2),
                    type=TransactionType.EXPENSE,
                    category="Groceries",
                    account="Credit Card",
                    note=random.choice(["Supermarket", "Farmer's Market", "Costco", "Trader Joe's"]),
                    tags=["food", "essential"]
                )
            )

        # Dining out: 2-3 times a week
        if random.random() < 0.35:
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(14.0, 75.0), 2),
                    type=TransactionType.EXPENSE,
                    category="Dining Out",
                    account="Credit Card",
                    note=random.choice(["Coffee Shop", "Lunch with colleagues", "Dinner date", "Takeout"]),
                    tags=["food", "lifestyle"]
                )
            )

        # Transportation / Gas: once or twice a week
        if random.random() < 0.25:
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(22.0, 55.0), 2),
                    type=TransactionType.EXPENSE,
                    category="Transportation",
                    account="Credit Card",
                    note=random.choice(["Gas Station", "Metro Card", "Uber Ride"]),
                    tags=["transport"]
                )
            )

        # Shopping or Entertainment: occasionally
        if random.random() < 0.15:
            transactions.append(
                Transaction(
                    id=str(uuid.uuid4())[:8],
                    date=curr_date,
                    amount=round(random.uniform(25.0, 160.0), 2),
                    type=TransactionType.EXPENSE,
                    category="Shopping",
                    account="Credit Card",
                    note=random.choice(["Clothing store", "Amazon order", "Electronics accessory", "Bookstore"]),
                    tags=["shopping"]
                )
            )

        curr_date += timedelta(days=1)

    # 5. Inject a couple of realistic anomalies (outliers) for testing ML anomaly detection
    # Anomaly 1: Unusually large electronics purchase 45 days ago
    anomaly_date_1 = end_date - timedelta(days=45)
    transactions.append(
        Transaction(
            id=str(uuid.uuid4())[:8],
            date=anomaly_date_1,
            amount=1899.00,
            type=TransactionType.EXPENSE,
            category="Shopping",
            account="Credit Card",
            note="New Laptop Purchase (Outlier)",
            tags=["anomaly", "equipment"]
        )
    )

    # Anomaly 2: Dental emergency 20 days ago
    anomaly_date_2 = end_date - timedelta(days=20)
    transactions.append(
        Transaction(
            id=str(uuid.uuid4())[:8],
            date=anomaly_date_2,
            amount=850.00,
            type=TransactionType.EXPENSE,
            category="Healthcare",
            account="Credit Card",
            note="Emergency Dental Treatment (Outlier)",
            tags=["anomaly", "health"]
        )
    )

    # Sort transactions by date ascending
    transactions.sort(key=lambda x: x.date)
    return transactions
