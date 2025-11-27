# FlowMarket - USSD SMS Marketing Platform

A complete Django application for USSD-based SMS campaign management using Africa's Talking API.

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

**Dial**: `*384*10688#`

```
FlowMarket Main Menu:
1. Create Campaign    - Create and save SMS campaign templates
2. Send Campaign      - Send campaigns to contact lists
3. Create New List    - Information about CSV upload
4. View Saved List    - View contact lists and details
```

**Full USSD Journey Documentation**: See [USSD_GUIDE.md](USSD_GUIDE.md) for complete flow details.

## 🔧 Project Structure

```
Flow-Market/
├── manage.py
├── requirements.txt
├── README.md
├── USSD_GUIDE.md              # Complete USSD flow documentation
├── IMPLEMENTATION_SUMMARY.md   # Detailed implementation guide
├── mainproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── app/
    ├── __init__.py
    ├── models.py              # Contact, Product, CampaignTemplate, ContactList, SentCampaign
    ├── views.py               # USSD logic, API endpoints
    ├── urls.py                # App routing
    ├── admin.py               # Django admin for all models
    ├── serializer.py          # Product serializer
    └── migrations/
```

## 📊 Managing Data

### Via Django Admin (`http://localhost:8000/admin/`)

1. **Contacts** - Add contacts with phone numbers (+254XXXXXXXXX format)
2. **Contact Lists** - Group contacts (e.g., "VIP Contacts", "Test List")
3. **Campaign Templates** - Pre-created SMS campaigns
4. **Sent Campaigns** - View history of sent campaigns
5. **Products** - Manage product catalog

### Via USSD (`*384*10688#`)

1. **Create campaigns** - Via option 1
2. **Send campaigns** - Via option 2
3. **View lists** - Via option 4

## 🔗 API Endpoints

- **Home Page**: `http://localhost:8000/` - Dashboard with stats
- **USSD Webhook**: `POST /ussd/` - Handles USSD menu interactions
- **Products API**: `GET /products/` - Returns products as JSON
- **Send Campaign**: `GET /send-campaign/` - Manual bulk SMS trigger
- **Admin Panel**: `http://localhost:8000/admin/` - Data management

## 📝 Testing

### 1. Add Sample Data (Django Admin)
1. Create contact lists: "All Contacts", "VIP Contacts", "Test List"
2. Add contacts to lists with phone numbers
3. Create campaign templates with sample messages

### 2. Test USSD Flow
1. Dial `*384*10688#` from your phone
2. Navigate through the menu
3. Create a campaign (Option 1)
4. Send a campaign (Option 2) to your Test List

### 3. Monitor Results
- Check sent campaigns in Django Admin
- View Africa's Talking dashboard for delivery status
- Check Django server logs for debugging

## 📚 Documentation

- **[USSD_GUIDE.md](USSD_GUIDE.md)** - Complete USSD flow walkthrough with examples
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **This README** - Quick start and setup guide

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
