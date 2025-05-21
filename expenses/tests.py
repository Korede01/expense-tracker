# tests.py
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import base64
from datetime import timedelta

from .models import Expense
from .serializers import ExpenseSerializer
from .filters import ExpenseFilter
from .reports import generate_spending_chart

User = get_user_model()


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='Test User', password='securepass123')
        self.expense = Expense.objects.create(
            user=self.user,
            amount='123.45',
            category='GROCERIES',
            date=timezone.now().date(),
            description='Weekly grocery'
        )

    def test_str(self):
        s = str(self.expense)
        self.assertIn('GROCERIES', s)
        self.assertIn('123.45', s)
        self.assertIn(str(self.expense.date), s)

    def test_indexes_and_ordering(self):
        meta = Expense._meta
        index_fields = [tuple(idx.fields) for idx in meta.indexes]
        self.assertIn(('user', 'date'), index_fields)
        self.assertIn(('category',), index_fields)
        self.assertEqual(meta.ordering, ['-date'])


class ExpenseSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='expense@example.com', name='Expense', password='securepass123')
        self.default_data = {
            'amount': '50.00',
            'category': 'utilities',
            'date': timezone.now().date(),
            'description': 'Bill'
        }

    def test_valid_payload(self):
        serializer = ExpenseSerializer(data=self.default_data, context={'request': type('r', (), {'user': self.user})})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        expense = serializer.save()
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.category, 'UTILITIES')

    def test_amount_validation(self):
        for invalid in [0, -10, 1_000_001]:
            data = self.default_data.copy()
            data['amount'] = invalid
            serializer = ExpenseSerializer(data=data, context={'request': type('r', (), {'user': self.user})})
            self.assertFalse(serializer.is_valid())
            self.assertIn('amount', serializer.errors)

    def test_date_validation(self):
        future = timezone.now().date() + timedelta(days=1)
        old = timezone.now().date() - timedelta(days=365*5 + 1)
        for date in [future, old]:
            data = self.default_data.copy()
            data['date'] = date
            serializer = ExpenseSerializer(data=data, context={'request': type('r', (), {'user': self.user})})
            self.assertFalse(serializer.is_valid())
            self.assertIn('date', serializer.errors)

    def test_category_validation(self):
        data = self.default_data.copy()
        data['category'] = 'invalid_cat'
        serializer = ExpenseSerializer(data=data, context={'request': type('r', (), {'user': self.user})})
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)


class ExpenseFilterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='filter@example.com', name='fiter', password='securepass123')
        today = timezone.now().date()
        Expense.objects.create(user=self.user, amount='10.00', category='GROCERIES', date=today - timedelta(days=2))
        Expense.objects.create(user=self.user, amount='20.00', category='UTILITIES', date=today - timedelta(days=1))
        Expense.objects.create(user=self.user, amount='30.00', category='ENTERTAINMENT', date=today)

    def test_date_range(self):
        qs = Expense.objects.filter(user=self.user)
        f = ExpenseFilter({'start_date': (timezone.now().date() - timedelta(days=1)).isoformat(),
                           'end_date': timezone.now().date().isoformat()}, queryset=qs)
        filtered = f.qs
        self.assertEqual(filtered.count(), 2)

    def test_invalid_date_range(self):
        qs = Expense.objects.filter(user=self.user)
        with self.assertRaises(ValidationError):
            ExpenseFilter({'start_date': '2025-01-10', 'end_date': '2025-01-01'}, queryset=qs).qs

    def test_amount_range(self):
        qs = Expense.objects.filter(user=self.user)
        f = ExpenseFilter({'min_amount': '15', 'max_amount': '25'}, queryset=qs)
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first().category, 'UTILITIES')


class ReportsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='report@example.com', name='reporter', password='securepass123')

    def test_generate_spending_chart_empty(self):
        self.assertIsNone(generate_spending_chart(self.user))

    def test_generate_spending_chart_nonempty(self):
        Expense.objects.create(user=self.user, amount='5.00', category='GROCERIES', date=timezone.now().date())
        Expense.objects.create(user=self.user, amount='15.00', category='UTILITIES', date=timezone.now().date())
        chart_b64 = generate_spending_chart(self.user)
        # Should be valid base64 and decode to PNG header
        decoded = base64.b64decode(chart_b64)
        self.assertTrue(decoded.startswith(b'\x89PNG'))


class ExpenseAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='api@example.com', name='Api', password='securepass123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse('expense-list')

    def test_create_expense(self):
        data = {
            'amount': '100.00',
            'category': 'GROCERIES',
            'date': timezone.now().date().isoformat(),
            'description': 'Test'
        }
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 1)

    def test_summary_endpoint(self):
        # create two expenses
        for amt in ['10.00', '20.00']:
            Expense.objects.create(user=self.user, amount=amt, category='GROCERIES', date=timezone.now().date())
        url = reverse('expense-summary')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_expenses'], 30.00)
        self.assertEqual(resp.data['transaction_count'], 2)

    def test_spending_chart_endpoint(self):
        Expense.objects.create(user=self.user, amount='7.00', category='ENTERTAINMENT', date=timezone.now().date())
        url = reverse('expense-reports-spending-chart')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('chart', resp.data)
        self.assertIsNotNone(resp.data['chart'])
