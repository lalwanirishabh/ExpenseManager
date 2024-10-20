from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from users.models import User
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db import transaction

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
            print('Error in fetching user ({payeeId}) : ', str(e))
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