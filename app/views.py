"""
View functions for handling USSD and SMS operations
These functions respond to webhooks from Africa's Talking
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Contact, Campaign
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


@csrf_exempt
def ussd_callback(request):
    """
    USSD Webhook endpoint - receives requests from Africa's Talking
    
    This function handles the USSD menu flow:
    1. Welcome screen with options
    2. View contacts count
    3. Send SMS campaign
    4. Exit
    
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
        
        # Split the text to get user's selections
        # Example: "1*2" means user selected 1, then 2
        text_array = text.split('*') if text else []
        user_response = text_array[-1] if text_array else ''
        
        # Response string - starts with CON (continue) or END (finish)
        response = ""
        
        # =====================================================
        # USSD MENU LOGIC
        # =====================================================
        
        if text == '':
            # First interaction - show main menu
            response = "CON Welcome to MSEM Service\n"
            response += "1. Contacts Count\n"
            response += "2. Send Promo SMS\n"
            response += "3. Exit"
        
        elif text == '1':
            # User selected option 1 - Show contacts count
            contacts_count = Contact.objects.filter(is_active=True).count()
            response = f"END You have {contacts_count} active contacts."
        
        elif text == '2':
            # User selected option 2 - Send SMS campaign
            # This triggers the SMS sending
            result = send_sms_campaign()
            
            if result['success']:
                response = f"END Promo SMS is being sent to {result['count']} contacts."
            else:
                response = f"END Failed to send SMS: {result['message']}"
        
        elif text == '3':
            # User selected option 3 - Exit
            response = "END Goodbye! Thank you for using MSEM Service."
        
        else:
            # Invalid option - show error and main menu again
            response = "CON Invalid option. Please try again.\n"
            response += "1. Contacts Count\n"
            response += "2. Send Promo SMS\n"
            response += "3. Exit"
        
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
    Simple home page showing API endpoints
    """
    contacts_count = Contact.objects.filter(is_active=True).count()
    campaigns_count = Campaign.objects.count()
    
    html = f"""
    <html>
    <head>
        <title>MSEM Service - USSD & SMS</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            .info {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .endpoint {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            code {{ background: #eee; padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>🚀 MSEM Service - USSD & SMS Platform</h1>
        
        <div class="info">
            <h2>📊 Statistics</h2>
            <p><strong>Active Contacts:</strong> {contacts_count}</p>
            <p><strong>Campaigns Sent:</strong> {campaigns_count}</p>
        </div>
        
        <div class="info">
            <h2>📱 USSD Menu</h2>
            <p>Dial your USSD code to access the menu:</p>
            <ol>
                <li>View Contacts Count</li>
                <li>Send Promo SMS</li>
                <li>Exit</li>
            </ol>
        </div>
        
        <div class="info">
            <h2>🔗 API Endpoints</h2>
            
            <div class="endpoint">
                <h3>USSD Webhook</h3>
                <p><code>POST /ussd/</code></p>
                <p>Receives USSD requests from Africa's Talking</p>
            </div>
            
            <div class="endpoint">
                <h3>Send SMS Campaign</h3>
                <p><code>GET /send-campaign/</code></p>
                <p><a href="/send-campaign/">Click here to send campaign manually</a></p>
            </div>
            
            <div class="endpoint">
                <h3>Admin Panel</h3>
                <p><code>GET /admin/</code></p>
                <p><a href="/admin/">Manage Contacts & View Campaigns</a></p>
            </div>
        </div>
        
        <div class="info">
            <h2>📚 Quick Guide</h2>
            <ol>
                <li>Add contacts via <a href="/admin/">Django Admin</a></li>
                <li>Configure USSD callback URL in Africa's Talking dashboard</li>
                <li>Test the USSD menu by dialing your code</li>
                <li>Send SMS campaigns via USSD option 2 or <a href="/send-campaign/">this link</a></li>
            </ol>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)
