# Django + Africa's Talking USSD & SMS Project

A simple Django application for USSD menu and SMS campaign management using Africa's Talking API.

## 🚀 Quick Start Guide

### 1. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Africa's Talking Credentials
Edit `mainproject/settings.py` and add your credentials:
```python
AFRICASTALKING_USERNAME = 'sandbox'  # or your username
AFRICASTALKING_API_KEY = 'your_api_key_here'
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (for Django Admin)
```bash
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

The server will run at: `http://localhost:8000`

### 7. Configure Africa's Talking Sandbox

1. Go to [Africa's Talking Dashboard](https://account.africastalking.com/)
2. Navigate to USSD → Sandbox
3. Set your callback URL to: `http://your-public-url/ussd/`
   - For local testing, use [ngrok](https://ngrok.com/): `ngrok http 8000`
   - Then use the ngrok URL: `https://your-ngrok-id.ngrok.io/ussd/`

## 📱 USSD Menu Flow

```
CON Welcome to MSEM Service
1. Contacts Count
2. Send Promo SMS
3. Exit

Option 1 → Shows total contacts
Option 2 → Sends SMS to all contacts
Option 3 → Exits the menu
```

## 🔧 Project Structure

```
Flow-Market/
├── manage.py
├── requirements.txt
├── README.md
├── mainproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── app/
    ├── __init__.py
    ├── models.py      # Contact and Campaign models
    ├── views.py       # USSD and SMS endpoints
    ├── urls.py        # App routing
    ├── admin.py       # Django admin configuration
    └── migrations/
```

## 📊 Managing Contacts

1. Access Django Admin: `http://localhost:8000/admin/`
2. Login with your superuser credentials
3. Add contacts with phone numbers (format: +254XXXXXXXXX)

## 🔗 API Endpoints

- **USSD Webhook**: `POST /ussd/` - Handles USSD menu interactions
- **Send SMS Campaign**: `GET /send-campaign/` - Sends bulk SMS to all contacts

## 📝 Testing

1. Add some contacts via Django Admin
2. Dial the USSD code from your Africa's Talking sandbox
3. Navigate through the menu
4. Option 2 will trigger SMS sending to all contacts

## 🛠️ Troubleshooting

**CSRF Token Errors**: The USSD endpoint is exempt from CSRF validation as it receives POST requests from Africa's Talking.

**SMS Not Sending**: 
- Verify your API credentials in settings.py
- Check that phone numbers are in international format (+254...)
- Review Africa's Talking sandbox limits

**Database Issues**: 
- Delete `db.sqlite3` and run migrations again
- Make sure migrations folder exists in the app

## 📚 Additional Resources

- [Africa's Talking Python SDK](https://github.com/AfricasTalkingLtd/africastalking-python)
- [Django Documentation](https://docs.djangoproject.com/)
- [Africa's Talking API Docs](https://developers.africastalking.com/)

## ⚠️ Important Notes

- This is a **development/demo project** - not production-ready
- Uses SQLite (replace with PostgreSQL/MySQL for production)
- No background tasks (consider Celery for production SMS)
- USSD webhook must be publicly accessible (use ngrok for local testing)

## 📄 License

This project is for educational/hackathon purposes.
