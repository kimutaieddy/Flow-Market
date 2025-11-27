# FlowMarket USSD Journey Guide

## Overview
FlowMarket is an SMS marketing platform accessible via USSD. Users can create campaigns, send them to contact lists, and manage their marketing efforts.

## USSD Code
`*384*10688#`

## Complete USSD Flow

### Main Menu
```
Welcome to FlowMarket. Please select:
1. Create Campaign
2. Send Campaign
3. Create New List (Upload via CSV)
4. View Saved List
```

---

### 1. Create Campaign
**Purpose**: Create and save SMS campaign templates

**Flow**:
1. User selects option 1
2. System prompts: "Input text of your campaign:"
   - Example: "Hello [Name], we have amazing products..."
   - Option 1: Cancel
3. User enters campaign message
4. System prompts: "Enter campaign name:"
   - Option 1: Cancel
   - Option 2: Save
5. User enters campaign name
6. System shows: "Confirm: 1. Cancel, 2. Save"
7. User selects 2 to save
8. System displays: "Your campaign has been successfully created and saved."

**Notes**:
- Use [Name] placeholder for personalization
- Campaigns are saved and can be reused
- Cancel option available at each step

---

### 2. Send Campaign
**Purpose**: Send a saved campaign to a contact list

**Flow**:
1. User selects option 2
2. System shows list of saved campaigns:
   ```
   Please select a campaign:
   1. New Product
   2. Valentines Hampers
   3. Christmas Boquetes
   4. Cancel
   ```
3. User selects a campaign
4. System shows contact lists:
   ```
   Select Contacts to receive campaign:
   1. All Contacts (1234)
   2. VIP Contacts (200)
   3. Test List (20)
   4. Cancel
   ```
5. User selects a contact list
6. System shows preview:
   ```
   Confirm message preview and send:
   "Buy X — 20% off!"
   
   1. Send now
   2. Cancel
   ```
7. User selects 1 to send
8. System displays: "Campaign sent successfully to X contacts!"

**Notes**:
- Shows actual contact count for each list
- Message preview limited to 100 characters
- Sends to all active contacts in the list
- Logs all sent campaigns with API response

---

### 3. Create New List (Upload via CSV)
**Purpose**: Inform users to upload contacts via web/app

**Flow**:
1. User selects option 3
2. System displays:
   ```
   Upload on FlowMarket Web Portal/App.
   
   1. OK
   2. Cancel
   ```
3. User selects 1
4. System displays: "We will notify you once your list is uploaded."

**Notes**:
- Actual CSV upload happens on web portal (not implemented yet)
- This is an informational flow
- Future enhancement: Direct CSV upload

---

### 4. View Saved List
**Purpose**: View existing contact lists and their details

**Flow**:
1. User selects option 4
2. System shows saved lists:
   ```
   Select list to view:
   1. All Contacts (1234)
   2. VIP Contacts (200)
   3. Test List (20)
   4. Back to main menu
   ```
3. User selects a list
4. System displays list details:
   ```
   VIP Contacts
   Total: 200 contacts
   Description: Premium customers
   ```

**Notes**:
- Shows total active contacts only
- Option to return to main menu
- Read-only view

---

## Setup Instructions for Testing

### 1. Add Sample Data via Django Admin

#### Create Contact Lists:
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to "Contact Lists"
3. Create lists:
   - **All Contacts** (add all contacts)
   - **VIP Contacts** (select specific contacts)
   - **Test List** (select 5-10 contacts for testing)

#### Create Campaign Templates:
1. Navigate to "Campaign Templates"
2. Create campaigns:
   - **New Product**: "Hello [Name], check out our new products at FlowMarket!"
   - **Valentines Hampers**: "Special Valentine's offer! Order your hamper today."
   - **Christmas Boquetes**: "Get ready for Christmas with our beautiful bouquets!"

#### Add Contacts:
1. Navigate to "Contacts"
2. Add contacts with:
   - Name: Customer name
   - Phone: +254XXXXXXXXX (Kenya format)
   - Is Active: Checked

### 2. Test the USSD Flow

#### Test Campaign Creation:
1. Dial `*384*10688#`
2. Select 1 (Create Campaign)
3. Enter: "Flash sale! 50% off all items today only!"
4. Enter campaign name: "Flash Sale"
5. Select 2 to save
6. ✅ Campaign created successfully

#### Test Campaign Sending:
1. Dial `*384*10688#`
2. Select 2 (Send Campaign)
3. Select campaign (e.g., "New Product")
4. Select contact list (e.g., "Test List")
5. Confirm and select 1 (Send now)
6. ✅ SMS sent to all contacts in the list

#### Test View Saved Lists:
1. Dial `*384*10688#`
2. Select 4 (View Saved List)
3. Select a list to view details
4. ✅ See contact count and description

---

## Technical Details

### Models Created:
1. **Contact** - Store contact information
2. **Product** - Store product catalog
3. **CampaignTemplate** - Store campaign templates
4. **ContactList** - Group contacts into lists
5. **SentCampaign** - Log all sent campaigns

### Key Features:
- ✅ Session management for USSD navigation
- ✅ Multi-step campaign creation
- ✅ Campaign preview before sending
- ✅ Cancel option at every step
- ✅ Real-time contact count display
- ✅ Full campaign logging with API responses
- ✅ Django Admin for easy management

### API Endpoints:
- `POST /ussd/` - USSD webhook (for Africa's Talking)
- `GET /products/` - Products API (JSON)
- `GET /send-campaign/` - Manual campaign trigger
- `GET /admin/` - Django Admin panel

---

## Troubleshooting

### Issue: "No campaigns available"
**Solution**: Create campaign templates in Django Admin first

### Issue: "No active contacts in this list"
**Solution**: 
1. Add contacts to the contact list in Django Admin
2. Ensure contacts have `is_active = True`

### Issue: "Campaign sending failed"
**Solution**:
1. Check Africa's Talking API credentials in `settings.py`
2. Verify phone numbers are in correct format (+254...)
3. Check sandbox SMS limits

### Issue: USSD session timeout
**Solution**: USSD sessions timeout after 30-60 seconds. Restart by dialing the code again.

---

## Next Steps / Future Enhancements

1. **Web Portal**: Build a web interface for easier campaign management
2. **CSV Upload**: Direct CSV contact list upload
3. **Scheduled Campaigns**: Schedule campaigns for later sending
4. **Analytics**: Track campaign performance (open rates, responses)
5. **Personalization**: Better [Name] and [Field] placeholder support
6. **Message Templates**: Pre-defined message templates
7. **A/B Testing**: Test different campaign variations
8. **Delivery Reports**: Track individual SMS delivery status

---

## Support

For issues or questions:
1. Check Django server logs
2. Review Africa's Talking dashboard for API logs
3. Use Django Admin to inspect database records
4. Check ngrok forwarding status

---

**Happy Marketing! 🚀📱**
