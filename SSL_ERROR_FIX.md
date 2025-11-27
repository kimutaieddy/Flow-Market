# 🔧 SSL Error Fix Guide - Africa's Talking API

## The Error
```
❌ Failed to send: HTTPSConnectionPool(host='api.sandbox.africastalking.com', port=443): 
Max retries exceeded with url: /version1/messaging 
(Caused by SSLError(SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1032)')))
```

## Common Causes & Solutions

### 1. **Corporate/School Network Proxy** 🏢
**Problem:** Your network has a proxy or firewall blocking SSL connections

**Solution A:** Use a personal hotspot or different network
- Connect to mobile hotspot
- Try from home network
- Use a VPN if allowed

**Solution B:** Configure proxy settings (if you have proxy details)
```python
# In settings.py, add:
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
```

### 2. **Antivirus/Firewall Blocking** 🛡️
**Problem:** Security software is interfering with SSL connections

**Solution:**
1. Temporarily disable antivirus SSL scanning
2. Add Python to firewall exceptions
3. Add `api.sandbox.africastalking.com` to trusted sites

### 3. **Outdated SSL/TLS Libraries** 📚
**Problem:** Python's SSL library is outdated

**Solution:**
```powershell
# Upgrade certifi (SSL certificates)
pip install --upgrade certifi

# Upgrade urllib3
pip install --upgrade urllib3

# Reinstall requests
pip install --force-reinstall requests
```

### 4. **Africa's Talking API Credentials** 🔑
**Problem:** Using sandbox with wrong credentials

**Solution:** Verify your credentials in `mainproject/settings.py`:
```python
AFRICASTALKING_USERNAME = 'sandbox'  # Or your actual username
AFRICASTALKING_API_KEY = 'your-actual-api-key-here'
```

Get your credentials from: https://account.africastalking.com/apps/sandbox

### 5. **Network Restrictions** 🌐
**Problem:** Your ISP or network blocks certain ports/protocols

**Solution:**
- Try using mobile data instead of WiFi
- Connect via VPN
- Contact network administrator

## Quick Fixes to Try NOW

### Fix #1: Update SSL Libraries
```powershell
# In your terminal:
D:/at-hackthone/Flow-Market/.venv/Scripts/python.exe -m pip install --upgrade certifi urllib3 requests
```

### Fix #2: Test Connection
```powershell
# Run the diagnostic script:
D:/at-hackthone/Flow-Market/.venv/Scripts/python.exe test_africastalking.py
```

### Fix #3: Fix Phone Numbers
```powershell
# Run this to fix phone number format:
D:/at-hackthone/Flow-Market/.venv/Scripts/python.exe manage.py fix_phone_numbers
```

### Fix #4: Use Mobile Hotspot
The most common fix for SSL errors in development:
1. Enable mobile hotspot on your phone
2. Connect your computer to the hotspot
3. Try sending SMS again

### Fix #5: Check Credentials
1. Go to https://account.africastalking.com/apps/sandbox
2. Copy your API Key
3. Update `mainproject/settings.py` with the correct key

## Testing Without Real SMS

If you just want to test the USSD flow without actually sending SMS:

**Option 1:** Comment out SMS sending temporarily
```python
# In views.py, in send_campaign_to_list function:
# response = sms.send(message, recipients)  # Comment this line
response = {'status': 'success', 'recipients': recipients}  # Add this mock response
```

**Option 2:** Use sandbox mode
Sandbox mode logs messages but doesn't send real SMS. Already using sandbox? Check your API key.

## Still Not Working?

### Check These:
1. ✅ Are you on a corporate/school network? → Use mobile hotspot
2. ✅ Is antivirus blocking? → Disable temporarily
3. ✅ Are credentials correct? → Check Africa's Talking dashboard
4. ✅ Is internet working? → Test other HTTPS sites
5. ✅ Phone numbers correct format? → Run `fix_phone_numbers` command

### Alternative: Mock SMS for Development
Add this to your `.env` or settings:
```python
# For development only - skip real SMS sending
SKIP_SMS_SENDING = True
```

Then modify the send function:
```python
if settings.SKIP_SMS_SENDING:
    # Just log and return success
    return {
        'success': True,
        'message': 'Mock sending (development mode)',
        'count': len(recipients)
    }
```

## Contact Support

If nothing works:
- **Africa's Talking Support:** support@africastalking.com
- **Check Status:** https://status.africastalking.com/
- **Documentation:** https://developers.africastalking.com/

---

**Most Common Fix:** 🔥
> 90% of SSL errors in development are fixed by switching to a mobile hotspot or different network!
