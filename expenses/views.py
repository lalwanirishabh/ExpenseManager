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