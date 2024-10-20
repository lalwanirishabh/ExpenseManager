# Description
Daily Expenses Sharing Application (Convin backend intern assignment task)
## How to run locally
1. Clone the repository and go to the file directory
2. Installation
   ```
    pip install -r requirements.txt
    ```
3. Run tests
   ```
    python manage.py test 
   ```
4. Run the server
    ```
    python manage.py runserver
    ```
# Endpoints
## User Service
### `POST user/create`

Description: Create user

Example Request:
```json
{
    "name":"Yash Singal",
    "email":"yash2@gmail.com",
    "password":"testPass",
    "phone":"2389940093"
}
```
Example Response:
```json
{
    "message": "User created successfully",
    "user_id": 7
}
```
### `Get user/:userId`

Description: Get user by id

Example Response:
```json
{
    "id": 1,
    "name": "Yash Khaitaj",
    "email": "yash@gmail.com",
    "phone": "2389940293"
}
```
### `Delete user/delete/:userId`

Description: Delete user by id

Example Response:
``` json
{
    "success": "User deleted"
}
```

## Expense Service

### `POST expense/add/`

Description: Add expense

Example Request:
```json
{
    "description": "sample expenses",
    "amount": 2000.0,
    "currency": "INR",
    "date": "2024-10-20",
    "payeeId": "7",
    "paymentType": "exact",
    "participants": [
        {"userId": "8", "amount": 800},
        {"userId": "9", "amount": 650},
        {"userId": "10", "amount": 550}
    ]
}
```
Example Response:
```json
{
    "message": "Expense created"
}
```
### `Get expense/user/:userId`

Description: Get individual expenses

Example Response:
```json
{
    "expenses": [
        {
            "expense_id": 6,
            "description": "sample expenses",
            "amount": 2000.0,
            "currency": "INR",
            "date": "2024-10-20",
            "payer": "Yash Singal",
            "payment_type": "exact",
            "amount_paid": 2000.0
        }
    ],
    "total_owed": 0,
    "total_paid": 2000.0,
    "net_owed": 2000.0
}
```
### `GET expense/`

Description: Overall expense

Example Response:
``` json
{
    "expenses": [
        {
            "expense_id": 6,
            "description": "sample expenses",
            "amount": 2000.0,
            "currency": "INR",
            "date": "2024-10-20",
            "payer": "Yash Singal",
            "payment_type": "exact",
            "participants": [
                {
                    "user_id": 8,
                    "username": "Yash Singal",
                    "amount": 800.0
                },
                {
                    "user_id": 9,
                    "username": "Yash Singal",
                    "amount": 650.0
                },
                {
                    "user_id": 10,
                    "username": "Yash Singal",
                    "amount": 550.0
                }
            ]
        }
    ]
}
```
### `GET expense/balanceSheet/:userId`

Description: Downloads the balance sheet for a user
``` csv
Type,Expense ID,Description,Amount,Currency,Date,Payer Name,Payment Type,Amount Owed,Amount Paid
Individual,6,sample expenses,2000.0,INR,2024-10-20,Yash Singal,exact,0,2000.0
Type,Expense ID,Description,Amount,Currency,Date,Payer Name,Payment Type,ParticipantId,ParticipantName,Amount
Overall,6,sample expenses,2000.0,INR,2024-10-20,Yash Singal,exact,8,Yash Singal,800.0
Overall,6,sample expenses,2000.0,INR,2024-10-20,Yash Singal,exact,9,Yash Singal,650.0
Overall,6,sample expenses,2000.0,INR,2024-10-20,Yash Singal,exact,10,Yash Singal,550.0
```

