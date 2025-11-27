"""
View functions for handling USSD and SMS operations
These functions respond to webhooks from Africa's Talking
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Contact, Campaign, Product, CampaignTemplate, ContactList, SentCampaign
from .serializer import ProductSerializer
import africastalking
import json


# Initialize Africa's Talking SDK
# This uses the credentials from settings.py
africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)

# Get the SMS service
sms = africastalking.SMS

# Session storage for USSD (in production, use Redis or database)
ussd_sessions = {}


@csrf_exempt
def ussd_callback(request):
    """
    USSD Webhook endpoint - receives requests from Africa's Talking.

    FlowMarket Customer Journey:

    1️⃣ Main Menu
      - Create Campaign
      - Send Campaign
      - View Contact Lists
      - Customer Support

    2️⃣ Create Campaign
      - Enter campaign message
      - Enter campaign name
      - Confirm and save

    3️⃣ Send Campaign
      - Select campaign
      - Select contact list
      - Preview message
      - Confirm and send

    4️⃣ View Contact Lists
      - Show available lists

    5️⃣ Customer Support
      - Show contact info
    """
    if request.method != 'POST':
        return HttpResponse("This endpoint only accepts POST requests", status=405)

    # Get POST params from Africa's Talking
    session_id = request.POST.get('sessionId', '')
    phone_number = request.POST.get('phoneNumber', '')
    text = request.POST.get('text', '')

    # Initialize USSD session
    if session_id not in ussd_sessions:
        ussd_sessions[session_id] = {}
    session_data = ussd_sessions[session_id]

    # Split user input for navigation
    text_array = text.split('*') if text else []

    response = ""  # Default response

    # ==========================
    # MAIN MENU
    # ==========================
    if text == '':
        response = "CON Welcome to FlowMarket!\nSelect an option:\n"
        response += "1. Create Campaign\n"
        response += "2. Send Campaign\n"
        response += "3. View Contact Lists\n"
        response += "4. Customer Support"
        session_data.clear()  # Reset session

    # ==========================
    # CREATE CAMPAIGN FLOW
    # ==========================
    elif text.startswith('1'):
        response = handle_create_campaign_flow(text_array, session_data, phone_number)

    # ==========================
    # SEND CAMPAIGN FLOW
    # ==========================
    elif text.startswith('2'):
        response = handle_send_campaign_flow(text_array, session_data, phone_number)

    # ==========================
    # VIEW CONTACT LISTS
    # ==========================
    elif text.startswith('3'):
        response = handle_view_contact_lists(text_array, session_data)

    # ==========================
    # CUSTOMER SUPPORT
    # ==========================
    elif text.startswith('4'):
        response = "END Contact us:\nEmail: support@flowmarket.com\nPhone: +1234567890"

    # ==========================
    # INVALID INPUT
    # ==========================
    else:
        response = "END Invalid input. Please dial again."
        session_data.clear()

    return HttpResponse(response, content_type='text/plain')


# ==========================
# Helper functions for USSD flows
# ==========================
def handle_create_campaign_flow(text_array, session_data, phone_number):
    """
    Handles the "Create Campaign" journey
    """
    step = len(text_array)

    if step == 1:
        session_data['action'] = 'create_campaign'
        return "CON Create campaign \n" \
               " input text of your campaign"

    elif step == 2:
        # User entered campaign message
        session_data['campaign_message'] = text_array[-1]
        return "CON Enter campaign name"

    elif step == 3:
        # User entered campaign name
        campaign_message = session_data.get('campaign_message', '')
        campaign_name = text_array[-1] or 'Untitled Campaign'

        # Save CampaignTemplate
        CampaignTemplate.objects.create(
            name=campaign_name,
            message=campaign_message,
            created_by=phone_number
        )
        session_data.clear()
        return "END  Campaign created successfully!"


def handle_send_campaign_flow(text_array, session_data, phone_number):
    """
    Handles the "Send Campaign" journey
    """
    step = len(text_array)

    # Step 1: Show campaigns
    if step == 1:
        campaigns = CampaignTemplate.objects.filter(is_active=True)[:5]
        if not campaigns:
            return "END No campaigns available. Create one first."

        session_data['action'] = 'send_campaign'
        session_data['campaigns'] = [c.id for c in campaigns]
        response = "CON Select a campaign:\n"
        for idx, c in enumerate(campaigns, 1):
            response += f"{idx}. {c.name}\n"
        response += f"{len(campaigns) + 1}. Cancel"
        return response

    # Step 2: Select campaign and show contact lists
    elif step == 2:
        try:
            selection = int(text_array[-1]) - 1
            campaigns_ids = session_data.get('campaigns', [])
            if selection == len(campaigns_ids):
                session_data.clear()
                return "END Campaign sending cancelled."
            campaign_id = campaigns_ids[selection]
            session_data['selected_campaign_id'] = campaign_id

            # Show contact lists
            contact_lists = ContactList.objects.filter(is_active=True)
            if not contact_lists:
                return "END No contact lists available. Create one first."

            session_data['contact_lists'] = [cl.id for cl in contact_lists]
            response = "CON Select a contact list:\n"
            for idx, cl in enumerate(contact_lists, 1):
                response += f"{idx}. {cl.name} ({cl.contact_count()})\n"
            response += f"{len(contact_lists) + 1}. Cancel"
            return response
        except (ValueError, IndexError):
            session_data.clear()
            return "END Invalid selection."

    # Step 3: Preview message and confirm
    elif step == 3:
        try:
            selection = int(text_array[-1]) - 1
            contact_lists_ids = session_data.get('contact_lists', [])
            if selection == len(contact_lists_ids):
                session_data.clear()
                return "END Campaign sending cancelled."
            contact_list_id = contact_lists_ids[selection]
            session_data['selected_list_id'] = contact_list_id

            # Show preview
            campaign = CampaignTemplate.objects.get(id=session_data['selected_campaign_id'])
            preview = campaign.message[:100] + '...' if len(campaign.message) > 100 else campaign.message
            return f"CON Preview message:\n\"{preview}\"\n\n1. Send Now\n2. Cancel"
        except Exception:
            session_data.clear()
            return "END Invalid selection."

    # Step 4: Send campaign
    elif step == 4:
        choice = text_array[-1]
        if choice == '1':
            try:
                campaign = CampaignTemplate.objects.get(id=session_data['selected_campaign_id'])
                contact_list = ContactList.objects.get(id=session_data['selected_list_id'])
                result = send_campaign_to_list(campaign, contact_list, phone_number)
                session_data.clear()
                if result['success']:
                    return f"END ✅ Campaign sent to {result['count']} contacts."
                else:
                    return f"END ❌ Failed to send: {result['message']}"
            except Exception as e:
                session_data.clear()
                return f"END ❌ Error: {str(e)}"
        elif choice == '2':
            session_data.clear()
            return "END Campaign sending cancelled."
        else:
            session_data.clear()
            return "END Invalid selection."


def handle_view_contact_lists(text_array, session_data):
    """
    Handles the "View Contact Lists" journey
    """
    step = len(text_array)

    # Step 1: Show all contact lists
    if step == 1:
        contact_lists = ContactList.objects.filter(is_active=True)
        if not contact_lists:
            return "END No contact lists available."

        session_data['action'] = 'view_lists'
        session_data['lists'] = [cl.id for cl in contact_lists]
        response = "CON Select a list to view:\n"
        for idx, cl in enumerate(contact_lists, 1):
            response += f"{idx}. {cl.name} ({cl.contact_count()})\n"
        response += f"{len(contact_lists) + 1}. Back to Main Menu"
        return response

    # Step 2: Show list details
    elif step == 2:
        try:
            selection = int(text_array[-1]) - 1
            lists_ids = session_data.get('lists', [])
            if selection == len(lists_ids):
                session_data.clear()
                return "CON Welcome to FlowMarket!\nSelect an option:\n1. Create Campaign\n2. Send Campaign\n3. View Contact Lists\n4. Customer Support"
            
            contact_list = ContactList.objects.get(id=lists_ids[selection])
            session_data.clear()
            return f"END {contact_list.name}\nTotal: {contact_list.contact_count()} contacts\nDescription: {contact_list.description or 'N/A'}"
        except (ValueError, IndexError, ContactList.DoesNotExist):
            session_data.clear()
            return "END Invalid selection."


# ==========================
# SMS Sending Functions
# ==========================
def send_campaign_to_list(campaign_template, contact_list, sent_by_phone):
    """
    Send a campaign to a specific contact list
    
    Args:
        campaign_template: CampaignTemplate object
        contact_list: ContactList object
        sent_by_phone: Phone number of user sending the campaign
    
    Returns:
        Dictionary with success status and details
    """
    message = None
    recipients = []
    
    try:
        # Get all active contacts in the list
        contacts = contact_list.contacts.filter(is_active=True)
        
        if not contacts.exists():
            return {
                'success': False,
                'message': 'No active contacts in this list',
                'count': 0
            }
        
        # Get phone numbers and validate format
        for contact in contacts:
            phone = contact.phone_number.strip()
            # Ensure phone number starts with +254
            if not phone.startswith('+'):
                if phone.startswith('254'):
                    phone = '+' + phone
                elif phone.startswith('0'):
                    phone = '+254' + phone[1:]
                else:
                    phone = '+254' + phone
            recipients.append(phone)
        
        # Use campaign message
        message = campaign_template.message
        
        # Log attempt before sending
        print(f"[SMS] Sending to {len(recipients)} contacts: {recipients[:3]}...")
        
        # Send SMS using Africa's Talking
        response = sms.send(message, recipients)
        
        print(f"[SMS] Response: {response}")
        
        # Log the sent campaign
        sent_campaign = SentCampaign.objects.create(
            campaign_template=campaign_template,
            contact_list=contact_list,
            message=message,
            recipients_count=len(recipients),
            sent_by=sent_by_phone,
            api_response=json.dumps(response, default=str),
            status='success'
        )
        
        return {
            'success': True,
            'message': 'Campaign sent successfully',
            'count': len(recipients),
            'response': response
        }
        
    except Exception as e:
        # Detailed error logging
        error_message = str(e)
        error_type = type(e).__name__
        
        print(f"[SMS ERROR] Type: {error_type}")
        print(f"[SMS ERROR] Message: {error_message}")
        
        # Log failed attempt
        SentCampaign.objects.create(
            campaign_template=campaign_template,
            contact_list=contact_list,
            message=message if message else 'Error occurred before sending',
            recipients_count=len(recipients),
            sent_by=sent_by_phone,
            api_response=f"{error_type}: {error_message}",
            status='failed'
        )
        
        # Return user-friendly error message
        if 'SSL' in error_message:
            friendly_message = 'Network security error. Check your internet connection.'
        elif 'Connection' in error_message:
            friendly_message = 'Cannot connect to SMS service. Try again later.'
        elif 'Invalid phone' in error_message:
            friendly_message = 'Invalid phone number format detected.'
        else:
            friendly_message = 'SMS service unavailable. Please try again.'
        
        return {
            'success': False,
            'message': friendly_message,
            'count': 0,
            'technical_error': error_message
        }


def send_sms_campaign():
    """
    Helper function to send SMS to all active contacts (legacy function)
    Returns a dictionary with success status and message
    """
    try:
        # Get all active contacts
        contacts = Contact.objects.filter(is_active=True)
        
        if not contacts.exists():
            return {
                'success': False,
                'message': 'No active contacts found',
                'count': 0
            }
        
        # Get phone numbers as a list
        recipients = [contact.phone_number for contact in contacts]
        
        # The SMS message to send
        message = "Hello! This is a promotional message from FlowMarket. Thank you for being our valued customer!"
        
        # Send SMS using Africa's Talking
        response = sms.send(message, recipients)
        
        # Log the campaign in database
        campaign = Campaign.objects.create(
            message=message,
            recipients_count=len(recipients),
            api_response=json.dumps(response, default=str),
            status='success'
        )
        
        return {
            'success': True,
            'message': 'SMS sent successfully',
            'count': len(recipients),
            'response': response
        }
        
    except Exception as e:
        # If something goes wrong, log it
        Campaign.objects.create(
            message=message if 'message' in locals() else 'Error occurred before message creation',
            recipients_count=len(recipients) if 'recipients' in locals() else 0,
            api_response=str(e),
            status='failed'
        )
        
        return {
            'success': False,
            'message': str(e),
            'count': 0
        }


@csrf_exempt
def send_campaign_view(request):
    """
    Manual endpoint to trigger SMS campaign
    Can be accessed via browser or API call
    
    Usage: GET http://localhost:8000/send-campaign/
    """
    result = send_sms_campaign()
    
    if result['success']:
        return HttpResponse(
            f"✅ Campaign sent successfully to {result['count']} contacts!\n\n"
            f"Details: {json.dumps(result['response'], indent=2, default=str)}",
            content_type='text/plain'
        )
    else:
        return HttpResponse(
            f"❌ Campaign failed: {result['message']}",
            content_type='text/plain',
            status=500
        )


# ==========================
# Home Page and API Views
# ==========================
def home(request):
    """
    Simple home page showing API endpoints and statistics
    """
    contacts_count = Contact.objects.filter(is_active=True).count()
    campaigns_count = Campaign.objects.count()
    campaign_templates_count = CampaignTemplate.objects.filter(is_active=True).count()
    contact_lists_count = ContactList.objects.filter(is_active=True).count()
    sent_campaigns_count = SentCampaign.objects.count()
    products_count = Product.objects.filter(is_active=True).count()
    
    html = f"""
    <html>
    <head>
        <title>FlowMarket - USSD SMS Marketing Platform</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f5f5f5; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
            .info {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-box h3 {{ margin: 0; font-size: 2.5em; }}
            .stat-box p {{ margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9; }}
            .endpoint {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #4caf50; }}
            .endpoint h3 {{ margin-top: 0; color: #2e7d32; }}
            code {{ background: #263238; color: #aed581; padding: 3px 8px; border-radius: 3px; font-family: 'Courier New', monospace; }}
            .ussd-code {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; font-size: 1.5em; margin: 20px 0; }}
            .feature {{ background: #fff3e0; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ff9800; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .warning {{ background: #ffebee; padding: 15px; border-radius: 5px; border-left: 4px solid #f44336; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 FlowMarket - USSD SMS Marketing Platform</h1>
            
            <div class="ussd-code">
                📱 USSD Code: <strong>*384*10688#</strong>
            </div>
            
            <div class="stats">
                <div class="stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h3>{contacts_count}</h3>
                    <p>Active Contacts</p>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h3>{campaign_templates_count}</h3>
                    <p>Campaign Templates</p>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h3>{contact_lists_count}</h3>
                    <p>Contact Lists</p>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <h3>{sent_campaigns_count}</h3>
                    <p>Campaigns Sent</p>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                    <h3>{products_count}</h3>
                    <p>Products</p>
                </div>
            </div>
            
            <div class="info">
                <h2>📱 USSD Menu Features</h2>
                <div class="feature">
                    <h3>1. Create Campaign</h3>
                    <p>Create and save SMS campaign templates for later use. Supports [Name] personalization.</p>
                </div>
                <div class="feature">
                    <h3>2. Send Campaign</h3>
                    <p>Select a saved campaign and send it to a contact list. Preview message before sending.</p>
                </div>
                <div class="feature">
                    <h3>3. View Contact Lists</h3>
                    <p>View your contact lists with total contact counts and descriptions.</p>
                </div>
                <div class="feature">
                    <h3>4. Customer Support</h3>
                    <p>Get contact information for customer support.</p>
                </div>
            </div>
            
            <div class="info">
                <h2>🔗 API Endpoints</h2>
                
                <div class="endpoint">
                    <h3>USSD Webhook</h3>
                    <p><code>POST /ussd/</code></p>
                    <p>Receives USSD requests from Africa's Talking. Callback URL: <code>https://videogenic-unprayerfully-kathe.ngrok-free.dev/ussd</code></p>
                </div>
                
                <div class="endpoint">
                    <h3>Products API</h3>
                    <p><code>GET /products/</code></p>
                    <p>Returns all active products as JSON. <a href="/products/">View Products →</a></p>
                </div>
                
                <div class="endpoint">
                    <h3>Send SMS Campaign (Manual)</h3>
                    <p><code>GET /send-campaign/</code></p>
                    <p>Manually trigger SMS to all contacts. <a href="/send-campaign/">Send Campaign →</a></p>
                </div>
                
                <div class="endpoint">
                    <h3>Admin Panel</h3>
                    <p><code>GET /admin/</code></p>
                    <p>Manage all data: contacts, campaigns, products, lists. <a href="/admin/">Open Admin →</a></p>
                </div>
            </div>
            
            <div class="info">
                <h2>📚 Quick Start Guide</h2>
                <ol>
                    <li><strong>Add Contacts:</strong> Go to <a href="/admin/">Admin Panel</a> → Contacts</li>
                    <li><strong>Create Contact Lists:</strong> Admin → Contact Lists (e.g., "VIP Contacts", "Test List")</li>
                    <li><strong>Add Sample Campaigns:</strong> Admin → Campaign Templates</li>
                    <li><strong>Test USSD:</strong> Dial <code>*384*10688#</code> from your phone</li>
                    <li><strong>Create Campaign:</strong> Follow USSD menu to create a new campaign</li>
                    <li><strong>Send Campaign:</strong> Select campaign and contact list to send SMS</li>
                </ol>
            </div>
            
            <div class="warning">
                <h2>⚠️ Important Setup</h2>
                <p><strong>Before testing:</strong></p>
                <ul>
                    <li>✅ Add your Africa's Talking API credentials in <code>mainproject/settings.py</code></li>
                    <li>✅ Create contact lists with active contacts</li>
                    <li>✅ Create at least one campaign template</li>
                    <li>✅ Ensure ngrok is running and forwarding to port 8000</li>
                    <li>✅ Configure USSD callback URL in Africa's Talking dashboard</li>
                </ul>
            </div>
            
            <div class="info">
                <h2>📖 Documentation</h2>
                <ul>
                    <li><strong>Main README:</strong> <code>README.md</code> - Project overview and installation</li>
                    <li><strong>USSD Guide:</strong> <code>USSD_GUIDE.md</code> - Complete USSD flow documentation</li>
                    <li><strong>API Docs:</strong> This page shows all available endpoints</li>
                </ul>
            </div>
            
            <div class="info" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <h2 style="color: white; border: none;">🎉 Ready to Market!</h2>
                <p>Your FlowMarket USSD SMS platform is ready. Start by adding contacts and creating your first campaign!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)


# =============================
# Products API View
# =============================
from django.http import JsonResponse

def products_list(request):
    """
    Returns all products as JSON for the frontend
    """
    products = Product.objects.filter(is_active=True)
    data = [ProductSerializer(product).to_dict() for product in products]
    return JsonResponse(data, safe=False)
