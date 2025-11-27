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
    USSD Webhook endpoint - receives requests from Africa's Talking
    
    FlowMarket USSD Journey:
    1. Welcome screen with main menu options
    2. Create Campaign - save SMS campaign template
    3. Send Campaign - select campaign and contact list to send
    4. Create New List - info about uploading via web/app
    5. View Saved List - view existing contact lists
    
    Africa's Talking sends these parameters:
    - sessionId: Unique session ID
    - serviceCode: Your USSD code
    - phoneNumber: User's phone number
    - text: User's input (empty on first request)
    """
    if request.method == 'POST':
        # Get parameters from Africa's Talking
        session_id = request.POST.get('sessionId', '')
        service_code = request.POST.get('serviceCode', '')
        phone_number = request.POST.get('phoneNumber', '')
        text = request.POST.get('text', '')
        
        # Split the text to get navigation path
        text_array = text.split('*') if text else []
        
        # Initialize session storage if not exists
        if session_id not in ussd_sessions:
            ussd_sessions[session_id] = {}
        
        session_data = ussd_sessions[session_id]
        
        # Response string - starts with CON (continue) or END (finish)
        response = ""
        
        # =====================================================
        # MAIN MENU - Welcome Screen
        # =====================================================
        if text == '':
            response = "CON Welcome to FlowMarket. Please select:\n"
            response += "1. Create Campaign\n"
            response += "2. Send Campaign\n"
            response += "3. Create New List (Upload via CSV)\n"
            response += "4. View Saved List"
        
        # =====================================================
        # OPTION 1: CREATE CAMPAIGN
        # =====================================================
        elif text == '1':
            # Show input screen for campaign text
            response = "CON Input text of your campaign:\n"
            response += "(e.g., Hello [Name], we have amazing products...)\n\n"
            response += "1. Cancel"
            session_data['action'] = 'create_campaign'
        
        elif text.startswith('1*') and session_data.get('action') == 'create_campaign':
            user_input = text.split('*', 1)[1]
            
            if user_input == '1':
                # Cancel - back to main menu
                response = "CON Welcome to FlowMarket. Please select:\n"
                response += "1. Create Campaign\n"
                response += "2. Send Campaign\n"
                response += "3. Create New List (Upload via CSV)\n"
                response += "4. View Saved List"
                session_data.clear()
            else:
                # Save campaign message temporarily
                session_data['campaign_message'] = user_input
                response = "CON Enter campaign name:\n"
                response += "1. Cancel\n"
                response += "2. Save"
        
        elif text.count('*') >= 2 and session_data.get('action') == 'create_campaign':
            parts = text.split('*')
            user_input = parts[-1]
            
            if user_input == '1':
                # Cancel
                response = "END Campaign creation cancelled."
                session_data.clear()
            elif user_input == '2':
                # Save the campaign
                campaign_message = session_data.get('campaign_message', '')
                campaign_name = parts[-2] if len(parts) >= 3 else 'Untitled Campaign'
                
                # Create campaign template
                CampaignTemplate.objects.create(
                    name=campaign_name,
                    message=campaign_message,
                    created_by=phone_number
                )
                
                response = "END Your campaign has been successfully created and saved."
                session_data.clear()
            else:
                # Treat as campaign name
                session_data['campaign_name'] = user_input
                response = "CON Confirm:\n"
                response += "1. Cancel\n"
                response += "2. Save"
        
        # =====================================================
        # OPTION 2: SEND CAMPAIGN
        # =====================================================
        elif text == '2':
            # Show list of saved campaigns
            campaigns = CampaignTemplate.objects.filter(is_active=True)[:3]
            
            if not campaigns:
                response = "END No campaigns available. Please create a campaign first."
            else:
                response = "CON Please select a campaign:\n"
                for idx, campaign in enumerate(campaigns, 1):
                    response += f"{idx}. {campaign.name}\n"
                response += f"{len(campaigns) + 1}. Cancel"
                session_data['action'] = 'send_campaign'
                session_data['campaigns'] = [c.id for c in campaigns]
        
        elif text.startswith('2*') and session_data.get('action') == 'send_campaign':
            parts = text.split('*')
            
            if len(parts) == 2:
                # User selected a campaign
                selection = parts[1]
                campaigns_ids = session_data.get('campaigns', [])
                
                try:
                    selection_idx = int(selection) - 1
                    if selection_idx == len(campaigns_ids):
                        # Cancel option
                        response = "END Campaign sending cancelled."
                        session_data.clear()
                    elif 0 <= selection_idx < len(campaigns_ids):
                        # Valid campaign selected
                        campaign_id = campaigns_ids[selection_idx]
                        session_data['selected_campaign_id'] = campaign_id
                        
                        # Show contact lists
                        contact_lists = ContactList.objects.filter(is_active=True)
                        
                        response = "CON Select Contacts to receive campaign:\n"
                        for idx, clist in enumerate(contact_lists, 1):
                            response += f"{idx}. {clist.name} ({clist.contact_count()})\n"
                        response += f"{len(contact_lists) + 1}. Cancel"
                        session_data['contact_lists'] = [cl.id for cl in contact_lists]
                    else:
                        response = "END Invalid selection."
                        session_data.clear()
                except ValueError:
                    response = "END Invalid input."
                    session_data.clear()
            
            elif len(parts) == 3:
                # User selected a contact list
                selection = parts[2]
                contact_lists_ids = session_data.get('contact_lists', [])
                
                try:
                    selection_idx = int(selection) - 1
                    if selection_idx == len(contact_lists_ids):
                        # Cancel option
                        response = "END Campaign sending cancelled."
                        session_data.clear()
                    elif 0 <= selection_idx < len(contact_lists_ids):
                        # Valid list selected
                        contact_list_id = contact_lists_ids[selection_idx]
                        session_data['selected_list_id'] = contact_list_id
                        
                        # Get campaign and show preview
                        campaign = CampaignTemplate.objects.get(id=session_data['selected_campaign_id'])
                        contact_list = ContactList.objects.get(id=contact_list_id)
                        
                        # Show preview (first 100 chars)
                        preview = campaign.message[:100] + '...' if len(campaign.message) > 100 else campaign.message
                        
                        response = "CON Confirm message preview and send:\n"
                        response += f"\"{preview}\"\n\n"
                        response += "1. Send now\n"
                        response += "2. Cancel"
                    else:
                        response = "END Invalid selection."
                        session_data.clear()
                except (ValueError, CampaignTemplate.DoesNotExist, ContactList.DoesNotExist):
                    response = "END Invalid selection."
                    session_data.clear()
            
            elif len(parts) == 4:
                # User confirmed or cancelled sending
                selection = parts[3]
                
                if selection == '1':
                    # Send now
                    try:
                        campaign = CampaignTemplate.objects.get(id=session_data['selected_campaign_id'])
                        contact_list = ContactList.objects.get(id=session_data['selected_list_id'])
                        
                        # Send SMS to all contacts in the list
                        result = send_campaign_to_list(campaign, contact_list, phone_number)
                        
                        if result['success']:
                            response = f"END Campaign sent successfully to {result['count']} contacts!"
                        else:
                            response = f"END Failed to send: {result['message']}"
                    except Exception as e:
                        response = f"END Error: {str(e)}"
                    
                    session_data.clear()
                elif selection == '2':
                    # Cancel
                    response = "END Campaign sending cancelled."
                    session_data.clear()
                else:
                    response = "END Invalid selection."
                    session_data.clear()
        
        # =====================================================
        # OPTION 3: CREATE NEW LIST
        # =====================================================
        elif text == '3':
            response = "CON Upload on FlowMarket Web Portal/App.\n\n"
            response += "1. OK\n"
            response += "2. Cancel"
            session_data['action'] = 'create_list'
        
        elif text.startswith('3*') and session_data.get('action') == 'create_list':
            selection = text.split('*')[1]
            if selection == '1':
                response = "END We will notify you once your list is uploaded."
            else:
                response = "END Cancelled."
            session_data.clear()
        
        # =====================================================
        # OPTION 4: VIEW SAVED LIST
        # =====================================================
        elif text == '4':
            # Show all saved contact lists
            contact_lists = ContactList.objects.filter(is_active=True)
            
            if not contact_lists:
                response = "END No saved lists available."
            else:
                response = "CON Select list to view:\n"
                for idx, clist in enumerate(contact_lists, 1):
                    response += f"{idx}. {clist.name} ({clist.contact_count()})\n"
                response += f"{len(contact_lists) + 1}. Back to main menu"
                session_data['action'] = 'view_list'
                session_data['lists'] = [cl.id for cl in contact_lists]
        
        elif text.startswith('4*') and session_data.get('action') == 'view_list':
            selection = text.split('*')[1]
            lists_ids = session_data.get('lists', [])
            
            try:
                selection_idx = int(selection) - 1
                if selection_idx == len(lists_ids):
                    # Back to main menu
                    response = "CON Welcome to FlowMarket. Please select:\n"
                    response += "1. Create Campaign\n"
                    response += "2. Send Campaign\n"
                    response += "3. Create New List (Upload via CSV)\n"
                    response += "4. View Saved List"
                    session_data.clear()
                elif 0 <= selection_idx < len(lists_ids):
                    # Show list details
                    contact_list = ContactList.objects.get(id=lists_ids[selection_idx])
                    response = f"END {contact_list.name}\n"
                    response += f"Total: {contact_list.contact_count()} contacts\n"
                    response += f"Description: {contact_list.description or 'N/A'}"
                    session_data.clear()
                else:
                    response = "END Invalid selection."
                    session_data.clear()
            except (ValueError, ContactList.DoesNotExist):
                response = "END Invalid selection."
                session_data.clear()
        
        # =====================================================
        # DEFAULT: INVALID INPUT
        # =====================================================
        else:
            response = "END Invalid input. Please dial again."
            session_data.clear()
        
        # Return response to Africa's Talking
        return HttpResponse(response, content_type='text/plain')
    
    else:
        # If not POST, return error
        return HttpResponse("This endpoint only accepts POST requests", status=405)


def send_sms_campaign():
    """
    Helper function to send SMS to all active contacts
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
        message = "Hello! This is a promotional message from MSEM Service. Thank you for being our valued customer!"
        
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
    try:
        # Get all active contacts in the list
        contacts = contact_list.contacts.filter(is_active=True)
        
        if not contacts.exists():
            return {
                'success': False,
                'message': 'No active contacts in this list',
                'count': 0
            }
        
        # Get phone numbers and personalize messages
        recipients = []
        for contact in contacts:
            recipients.append(contact.phone_number)
        
        # Replace [Name] placeholder with actual names (for now, send generic)
        message = campaign_template.message
        
        # Send SMS using Africa's Talking
        response = sms.send(message, recipients)
        
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
        # Log failed attempt
        SentCampaign.objects.create(
            campaign_template=campaign_template,
            contact_list=contact_list,
            message=message if 'message' in locals() else 'Error occurred',
            recipients_count=len(recipients) if 'recipients' in locals() else 0,
            sent_by=sent_by_phone,
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
                    <h3>3. Create New List</h3>
                    <p>Information about uploading contact lists via web portal/CSV.</p>
                </div>
                <div class="feature">
                    <h3>4. View Saved List</h3>
                    <p>View your contact lists with total contact counts and descriptions.</p>
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
