from .Singleton import Singleton
from ..models.transaction import Transaction
from datetime import date, datetime, timedelta
from .CacheManager import CacheManager
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION
from ..error_handling.logger import logger
from flask import current_app
import random
import uuid

CATEGORIES_INCOME = ['Pensja', 'Premia', 'Zwrot podatku', 'Sprzedaż']
CATEGORIES_EXPENSE = ['Jedzenie', 'Mieszkanie', 'Transport', 'Zdrowie', 'Rozrywka', 'Subskrypcje']

DESCRIPTIVE_NAMES_INCOME = [
    'Wypłata wynagrodzenia', 'Premia kwartalna', 'Zwrot z urzędu skarbowego', 'Sprzedaż starego roweru',
    'Odsetki z lokaty', 'Zwrot za paliwo', 'Dodatek stażowy', 'Prezent urodzinowy', 'Zlecenie freelance',
    'Sprzedaż na Vinted', 'Zwrot kaucji', 'Nagroda roczna'
]
DESCRIPTIVE_NAMES_EXPENSE = [
    'Zakupy Tesco', 'Wizyta u Dentysty', 'Paliwo Orlen', 'Czynsz za mieszkanie', 'Abonament Netflix',
    'Bilet do kina', 'Kawa Starbucks', 'Uber Eats', 'Zakupy Biedronka', 'Opłata za prąd',
    'Internet UPC', 'Siłownia karnet', 'Prezent dla mamy', 'Naprawa samochodu', 'Fryzjer',
    'Książki Empik', 'Spotify Premium', 'Pizza Dominos', 'Bilet miesięczny', 'Apteka leki'
]

class TransactionManager(metaclass=Singleton):

    def generate_transactions(self, user_id, count=100):
        items = []
        today = datetime.now()

        for i in range(count):
            is_income = random.random() < 0.4
            amount = random.randint(50, 5000) if is_income else random.randint(10, 300)

            days_ago = random.randint(0, 60)
            tx_date = today - timedelta(days=days_ago)
            date_str = tx_date.strftime("%Y-%m-%d")

            category = random.choice(CATEGORIES_INCOME) if is_income else random.choice(CATEGORIES_EXPENSE)
            name = random.choice(DESCRIPTIVE_NAMES_INCOME) if is_income else random.choice(DESCRIPTIVE_NAMES_EXPENSE)

            tx_id = f"{user_id}-{i}"

            items.append({
                "id": tx_id,
                "name": name,
                "amount": amount,
                "category": category,
                "type": 'income' if is_income else 'expense',
                "date": date_str
            })

        items.sort(key=lambda x: x['date'], reverse=True)
        return items

    def ensure_user_data(self, user_id):
        cache = CacheManager()
        print("TransactionManager calling CacheManager()")
        user = cache.get_user(user_id)
        if not user:
            logger.debug(f"There was no user {user_id}")
            return None

        if not user.get('transactions'):
            user['transactions'] = self.generate_transactions(user_id, 150)
            cache.set_user(user_id, user)

        return user['transactions']

    def list_transactions(self, user_id):
        return self.ensure_user_data(user_id)

    def get_dashboard_summary(self, user_id):
        transactions = self.ensure_user_data(user_id)
        if not transactions:
            logger.debug("transactions was empty :/")
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()
        first_day_month = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")

        today_tx = [t for t in transactions if t['date'] == today]
        month_tx = [t for t in transactions if t['date'] >= first_day_month and t['date'] <= today]

        income_daily = sum(t['amount'] for t in today_tx if t['type'] == 'income')
        expense_daily = sum(t['amount'] for t in today_tx if t['type'] == 'expense')

        income_monthly = sum(t['amount'] for t in month_tx if t['type'] == 'income')
        expense_monthly = sum(t['amount'] for t in month_tx if t['type'] == 'expense')

        return {
            "incomeDaily": income_daily,
            "expenseDaily": expense_daily,
            "balanceDaily": income_daily - expense_daily,
            "incomeMonthly": income_monthly,
            "expenseMonthly": expense_monthly,
            "balanceMonthly": income_monthly - expense_monthly
        }

    def get_recent_transactions(self, user_id):
        transactions = self.ensure_user_data(user_id)
        # Assuming already sorted desc by date in ensure/generate
        # But if added manually, might need sorting. Let's sort to be safe but expensive?
        # api.ts sorts on generation. addTransaction unshifts. So it should be sorted.
        return transactions[:5]

    def filter_transactions(self, user_id, date_from=None, date_to=None, name=None, category=None, amount_min=None, amount_max=None, sort=None):
        transactions = self.ensure_user_data(user_id)

        result = []
        for t in transactions:
            if date_from and t['date'] < date_from: continue
            if date_to and t['date'] > date_to: continue
            if name and name.lower() not in t['name'].lower(): continue
            if category and t['category'] != category: continue
            if amount_min is not None and t['amount'] < float(amount_min): continue
            if amount_max is not None and t['amount'] > float(amount_max): continue
            result.append(t)

        # Sorting
        if sort:
            if sort == 'amount-asc':
                result.sort(key=lambda x: x['amount'])
            elif sort == 'amount-desc':
                result.sort(key=lambda x: x['amount'], reverse=True)
            elif sort == 'date-asc':
                result.sort(key=lambda x: x['date'])
            elif sort == 'date-desc':
                result.sort(key=lambda x: x['date'], reverse=True)
        else:
            # Default desc date
            result.sort(key=lambda x: x['date'], reverse=True)

        return result

    def get_charts(self, user_id):
        self.ensure_user_data(user_id)
        # Mocking complex logic from api.ts because it generates random data for charts
        # largely independent of actual transaction history in api.ts (except for breakdown potentially)
        # But api.ts getCharts actually simply returns randomized data for most charts.
        # I will replicate the "random within range" logic to match the "simulation" aspect.

        def rand(min_val, max_val):
            return random.randint(min_val, max_val)

        def last_n_days(n):
            days = []
            today = datetime.now()
            for i in range(n-1, -1, -1):
                d = today - timedelta(days=i)
                days.append(d.strftime("%Y-%m-%d"))
            return days

        days = last_n_days(30)
        daily_income = [rand(0, 400) for _ in days]
        daily_expense = [rand(0, 350) for _ in days]
        daily_balance = [i - e for i, e in zip(daily_income, daily_expense)]

        weeks = [f"T-{12-i}" for i in range(12)]
        weekly_balance = [rand(-800, 1200) for _ in weeks]

        months = [f"M-{12-i}" for i in range(12)]
        monthly_balance = [rand(-2500, 4500) for _ in months]

        yearly_labels = [f"Month {i+1}" for i in range(12)]
        yearly_data = [rand(-5000, 8000) for _ in yearly_labels]

        half_yearly_labels = [f"Month {i+1}" for i in range(6)]
        half_yearly_data = [rand(-4000, 6000) for _ in half_yearly_labels]

        quarterly_labels = [f"Month {i+1}" for i in range(3)]
        quarterly_data = [rand(-3000, 5000) for _ in quarterly_labels]

        monthly_labels = days
        monthly_data = [rand(-500, 800) for _ in monthly_labels] # reusing days logic

        weekly_labels_unified = last_n_days(7)
        weekly_data_unified = [rand(-200, 400) for _ in weekly_labels_unified]

        avg_daily_income = int(sum(daily_income) / len(daily_income))
        avg_daily_expense = int(sum(daily_expense) / len(daily_expense))

        ranking = [{"category": c, "amount": rand(300, 2000)} for c in CATEGORIES_EXPENSE]
        ranking.sort(key=lambda x: x['amount'], reverse=True)

        return {
            "daily": {"labels": days, "income": daily_income, "expense": daily_expense, "balance": daily_balance},
            "weekly": {"labels": weeks, "balance": weekly_balance},
            "monthly": {"labels": months, "balance": monthly_balance},
            "unified": {
                "yearly": {"labels": yearly_labels, "data": yearly_data},
                "halfYearly": {"labels": half_yearly_labels, "data": half_yearly_data},
                "quarterly": {"labels": quarterly_labels, "data": quarterly_data},
                "monthly": {"labels": monthly_labels, "data": monthly_data},
                "weekly": {"labels": weekly_labels_unified, "data": weekly_data_unified}
            },
            "averages": {"avgDailyIncome": avg_daily_income, "avgDailyExpense": avg_daily_expense},
            "ranking": ranking
        }

    def get_category_breakdown(self, user_id, type_filter, period):
        transactions = self.ensure_user_data(user_id)
        now = datetime.now()
        start_date = now # placeholder

        if period == 'yearly':
            start_date = datetime(now.year, 1, 1)
        elif period == 'halfYearly':
            start_date = now - timedelta(days=6*30)
        elif period == 'quarterly':
            start_date = now - timedelta(days=3*30)
        elif period == 'monthly':
            start_date = datetime(now.year, now.month, 1)
        elif period == 'weekly':
            start_date = now - timedelta(days=7)

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = now.strftime("%Y-%m-%d")

        filtered = [t for t in transactions if t['type'] == type_filter and start_date_str <= t['date'] <= end_date_str]

        totals = {}
        for t in filtered:
            totals[t['category']] = totals.get(t['category'], 0) + t['amount']

        total_sum = sum(totals.values())

        result = []
        for cat, amount in totals.items():
            result.append({
                "category": cat,
                "amount": amount,
                "percentage": round((amount / total_sum) * 100) if total_sum > 0 else 0
            })

        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    def add_transaction(self, user_id, name, transaction_type, amount, category):
        cache = CacheManager()
        print("TransactionManager calling CacheManager()")
        # Use simpler logic without calling cache.add_transaction with object
        user = cache.get_user(user_id)
        if not user: raise Exception("User not found")

        if 'transactions' not in user:
            user['transactions'] = []

        new_tx = {
            "id": f"{user_id}-{int(datetime.now().timestamp() * 1000)}",
            "name": name,
            "type": transaction_type,
            "amount": amount,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        # Insert at beginning
        user['transactions'].insert(0, new_tx)

        # Update balance
        val = amount if transaction_type == 'income' else -amount
        user['funds'] += val

        cache.set_user(user_id, user)
        return new_tx

    def update_transaction(self, user_id, transaction_id, updates):
        cache = CacheManager()
        print("TransactionManager calling CacheManager()")
        user = cache.get_user(user_id)
        if not user: return None

        transactions = user.get('transactions', [])
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                # Calculate balance diff if amount/type changed?
                # For simplicity, let's assume complex balance recalc via full re-sum or just simple delta
                # Actually, api.ts doesn't explicitly track balance in user object, just aggregates.
                # User model has 'funds'. Let's update funds.

                old_val = t['amount'] if t['type'] == 'income' else -t['amount']

                updated_tx = {**t, **updates}
                transactions[i] = updated_tx

                new_val = updated_tx['amount'] if updated_tx['type'] == 'income' else -updated_tx['amount']
                user['funds'] += (new_val - old_val)

                cache.set_user(user_id, user)
                return updated_tx
        return None

    def delete_transaction(self, user_id, transaction_id):
        cache = CacheManager()
        print("TransactionManager calling CacheManager()")
        user = cache.get_user(user_id)
        if not user: return False

        transactions = user.get('transactions', [])
        for i, t in enumerate(transactions):
            if t['id'] == transaction_id:
                val = t['amount'] if t['type'] == 'income' else -t['amount']
                user['funds'] -= val
                transactions.pop(i)
                cache.set_user(user_id, user)
                return True
        return False
