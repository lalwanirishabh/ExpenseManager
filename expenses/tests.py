from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from users.models import User
from .models import Expense, Participant
from django.contrib.auth.hashers import make_password
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

class ExpenseAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        hash_pass = make_password("testPass")
        # Create a user for testing
        self.user = User.objects.create(name="Test User", email="test@gmail.com", phone="1234567890", password=hash_pass)
        self.user2 = User.objects.create(name="Test User", email="test2@gmail.com", phone="1334567890", password=hash_pass)
        self.user3 = User.objects.create(name="Test User", email="test3@gmail.com", phone="1434567890", password=hash_pass)

        # Create expenses and participants
        self.expense = Expense.objects.create(
            description="Dinner",
            amount=100,
            currency="USD",
            date="2024-10-20",
            payer=self.user,
            payment_type="exact"
        )
        self.participant = Participant.objects.create(
            expense=self.expense,
            user=self.user,
            amount=100
        )
        self.participant2 = Participant.objects.create(
            expense=self.expense,
            user=self.user2,
            amount=100
        )
        self.participant3 = Participant.objects.create(
            expense=self.expense,
            user=self.user3,
            amount=100
        )

    def test_create_expense_success(self):
        try:
            url = reverse('createExpense')
            data = {
                'description': 'Lunch',
                'amount': 50,
                'currency': 'USD',
                'date': '2024-10-20',
                'payeeId': self.user.id,
                'paymentType': 'exact',
                'participants': [{'userId': self.user.id, 'amount': 50}]
            }
            response = self.client.post(url, data, content_type='application/json')
            response_data = response.json()
            self.assertEqual(response_data['message'], 'Expense created')
            print(Fore.GREEN + "test_create_expense_success passed")
        except AssertionError as e:
            print(Fore.RED + "test_create_expense_success failed: " + str(e))

    def test_create_expense_missing_fields(self):
        try:
            url = reverse('createExpense')
            data = {
                'description': 'Lunch',
                'amount': 50,
                'currency': 'USD',
                'date': '2024-10-20',
                # 'payeeId' is missing
                'paymentType': 'exact',
                'participants': [{'userId': self.user.id, 'amount': 50}]
            }
            response = self.client.post(url, data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            response_data = response.json()
            self.assertEqual(response_data['error'], 'All fields are required')
            print(Fore.GREEN + "test_create_expense_missing_fields passed")
        except AssertionError as e:
            print(Fore.RED + "test_create_expense_missing_fields failed: " + str(e))

    def test_fetch_individual_expense(self):
        try:
            url = reverse('fetchIndividualExpenses', args=[self.user.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('expenses', response.json())
            print(Fore.GREEN + "test_fetch_individual_expense passed")
        except AssertionError as e:
            print(Fore.RED + "test_fetch_individual_expense failed: " + str(e))

    def test_get_overall_expense(self):
        try:
            url = reverse('getOverallExpenses')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('expenses', response.json())
            print(Fore.GREEN + "test_get_overall_expense passed")
        except AssertionError as e:
            print(Fore.RED + "test_get_overall_expense failed: " + str(e))

    def test_integration_create_and_fetch_expense(self):
        try:
            # step 1: create expense
            url = reverse('createExpense')
            data = {
                'description': 'Dinner',
                'amount': 100,
                'currency': 'USD',
                'date': '2024-10-20',
                'payeeId': self.user.id,
                'paymentType': 'exact',
                'participants': [{'userId': self.user.id, 'amount': 100}]
            }
            response = self.client.post(url, data, content_type='application/json')
            response_data = response.json()
            self.assertEqual(response_data['message'], 'Expense created')

            # step 2: fetch expense
            url = reverse('fetchIndividualExpenses', args=[self.user.id])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('expenses', response.json())
            print(Fore.GREEN + "test_integration_create_and_fetch_expense passed")
        except AssertionError as e:
            print(Fore.RED + "test_integration_create_and_fetch_expense failed " + str(e))

    def tearDown(self):
        # Clean up after tests if necessary
        self.user.delete()
        self.expense.delete()
        self.participant.delete()