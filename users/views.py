from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User 
from django.contrib.auth.hashers import make_password
from .serializer import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
import json

# Create your views here.
@api_view(['POST'])
def createUser(request):
    try :
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        if not (name and email and phone and password):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        if User.objects.filter(phone=phone).exists():
                return JsonResponse({'error': 'Phone number already exists'}, status=400)

        hash_pass = make_password(password)

        user = User.objects.create(name=name, email=email, phone=phone, password=hash_pass)
        return JsonResponse({'message': 'User created successfully', 'user_id': user.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def getUser(request,userId):
    try:
        # user = User.objects.filter(id=userId)
        user = get_object_or_404(User, id=userId)
        response_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone
        }
        return JsonResponse(response_data)
    except Exception as e:
#         print('Internal server error', str(e))
        return JsonResponse({'error': 'User not found'}, status=404)


@api_view(['DELETE'])
def deleteUser(request, userId):
    try:
        user = get_object_or_404(User, id=userId)
        user.delete()
        return JsonResponse({'success': 'User deleted'}, status = 200)
    except Exception as e:
#         print('Internal server error', str(e))
        return JsonResponse({'error': 'User not found'}, status=404)