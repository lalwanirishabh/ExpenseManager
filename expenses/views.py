from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from users.models import User
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import json
from django.urls import reverse
import csv
from django.db import transaction
import requests

BASE_URL = 'http://localhost:8000'

@api_view(['POST'])
def createExpense(request):
    try :
        data = json.loads(request.body)
        description = data.get('description')
        amount = data.get('amount')
        currency = data.get('currency')
        date = data.get('date')
        payeeId = data.get('payeeId')
        paymentType = data.get('paymentType')
        participants_data = data.get('participants')
        
        if not all([description, amount, currency, date, payeeId, paymentType, participants_data]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        try:
            payeeUser=get_object_or_404(User, id=int(payeeId))
        except Exception as e:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        
        total_amount = float(amount)
        exact_sum = 0
        percentage_sum = 0

        for participant_data in participants_data:
                if paymentType == "exact":
                    exact_sum += float(participant_data['amount']) 
                elif paymentType == "percentage":
                    percentage_sum += float(participant_data['amount'])
        if paymentType == "exact" and exact_sum != total_amount: # Check whether individual sums amount to total sum
                return JsonResponse({'error': 'Exact amounts do not sum up to the total expense amount'}, status=400)
        elif paymentType == "percentage" and percentage_sum != 100: # Check whether all percentages sum to 100
            print(f'Error in fetching user ({payeeId}) : ', str(e))
            return JsonResponse({'error': 'Percentages do not sum up to 100%'}, status=400)

        with transaction.atomic():
            expense = Expense.objects.create(
                description=description,
                amount=total_amount,
                currency=currency,
                date=date,
                payer=payeeUser,
                payment_type=paymentType
            )

            for participant_data in participants_data:
                user = User.objects.get(id=participant_data['userId'])
                if paymentType == "percentage":
                    participant_amount = (float(participant_data['amount']) / 100) * total_amount
                else:
                    participant_amount = float(participant_data['amount'])
                
                Participant.objects.create(expense=expense, user=user, amount=participant_amount)
            return JsonResponse({'message': 'Expense created'}, status=201)

    except Exception as e:
        print('Error in creating expense', str(e))
        return JsonResponse({'error': 'Internal server error'}, status=500)
    

@api_view(['GET'])
def fetchIndividualExpense(request, userId):
    try:
        user = get_object_or_404(User, id=userId)
        participants = Participant.objects.filter(user=user).exclude(expense__payer=user)
        expenses = Expense.objects.filter(payer=user)
        user_expenses = []

        total_owed = 0
        total_paid = 0

        for participant in participants:
            expense = participant.expense
            total_owed += participant.amount
            user_expenses.append({
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': expense.payer.name,
                'payment_type': expense.payment_type,
                'amount_owed': participant.amount
            })

        for expense in expenses:
            total_paid += expense.amount 
            user_expenses.append({
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': user.name,
                'payment_type': expense.payment_type,
                'amount_paid': expense.amount
            })

        net_owed = total_paid - total_owed
        return JsonResponse({
            'expenses': user_expenses,
            'total_owed': total_owed,
            'total_paid': total_paid,
            'net_owed': net_owed
        }, status=200, safe=False)
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print('Error in fecthing individual expense', str(e))
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['GET'])
def getOverallExpense(request):
    try :
        expenses = Expense.objects.all()
        all_expenses =[]

        for expense in expenses :
            participants = Participant.objects.filter(expense=expense)
            participants_info = []
            for participant in participants:
                participants_info.append({
                    'user_id': participant.user.id,
                    'username': participant.user.name,
                    'amount': participant.amount
                })
            
            all_expenses.append({
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': expense.payer.name,
                'payment_type': expense.payment_type,
                'participants': participants_info
            })
        return JsonResponse({'expenses': all_expenses}, status=200, safe=False)


    except Exception as e:
        print('Error in fecthing expenses', str(e))
        return JsonResponse({'error': str(e)}, status=500)
    


@api_view(['GET'])
def balanceSheet(request, userId=None):
    try :
        if userId:
                individual_expenses_url = reverse('fetchIndividualExpenses', args=[userId])
                individual_expenses_response = requests.get(f"{BASE_URL}{individual_expenses_url}")
                individual_expenses_response.raise_for_status()
                individual_expenses = individual_expenses_response.json()
        else:
            individual_expenses = {'expenses': []}

        overall_expenses_url = reverse('getOverallExpenses')
        overall_expenses_response = requests.get(f"{BASE_URL}{overall_expenses_url}") # Call Overall Expense
        overall_expenses_response.raise_for_status()
        overall_expenses = overall_expenses_response.json()
        print(f"Overall_expenses {overall_expenses}")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Type', 'Expense ID', 'Description', 'Amount', 'Currency', 'Date',
            'Payer Name', 'Payment Type', 'Amount Owed', 'Amount Paid'
        ])

        if userId:
            #Individual expenses
            for expense in individual_expenses['expenses']:
                amount_owed = expense.get('amount_owed', 0)
                amount_paid = expense.get('amount_paid', 0)
                writer.writerow([
                    'Individual',
                    expense['expense_id'],
                    expense['description'],
                    expense['amount'],
                    expense['currency'],
                    expense['date'],
                    expense['payer'],
                    expense['payment_type'],
                    amount_owed,
                    amount_paid
                ])
            
            writer.writerow([
                'Type', 'Expense ID', 'Description', 'Amount', 'Currency', 'Date',
                'Payer Name', 'Payment Type', 'ParticipantId' ,'ParticipantName' ,'Amount' 
            ])
            for expense in overall_expenses['expenses']:
                for participant in expense['participants']:
                    writer.writerow([
                        'Overall',
                        expense['expense_id'],
                        expense['description'],
                        expense['amount'],
                        expense['currency'],
                        expense['date'],
                        expense['payer'],
                        expense['payment_type'],
                        participant['user_id'],
                        participant['username'],
                        participant['amount']
                    ])

        return response

    except Exception as e:
        print('Error in generatign balance sheet', str(e))
        return JsonResponse({'error': str(e)}, status=500)
    