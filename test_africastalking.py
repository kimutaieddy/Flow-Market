"""
Test script to check Africa's Talking API connectivity
Run this to diagnose SSL/connection issues
"""
import africastalking
from django.conf import settings
import ssl
import socket

# Initialize Africa's Talking
africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)

sms = africastalking.SMS

print("=" * 60)
print("🔍 Africa's Talking API Connection Test")
print("=" * 60)

# Test 1: Check SSL/TLS support
print("\n1️⃣ Checking SSL/TLS support...")
try:
    print(f"   SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"   ✅ SSL is available")
except Exception as e:
    print(f"   ❌ SSL Error: {e}")

# Test 2: Check internet connectivity
print("\n2️⃣ Checking internet connectivity...")
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("   ✅ Internet connection OK")
except OSError:
    print("   ❌ No internet connection")

# Test 3: Check DNS resolution for Africa's Talking
print("\n3️⃣ Checking DNS resolution...")
try:
    host = "api.sandbox.africastalking.com"
    ip = socket.gethostbyname(host)
    print(f"   ✅ {host} resolves to {ip}")
except socket.gaierror as e:
    print(f"   ❌ DNS resolution failed: {e}")

# Test 4: Check SSL connection to Africa's Talking
print("\n4️⃣ Checking SSL connection...")
try:
    context = ssl.create_default_context()
    with socket.create_connection(("api.sandbox.africastalking.com", 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname="api.sandbox.africastalking.com") as ssock:
            print(f"   ✅ SSL connection successful")
            print(f"   Protocol: {ssock.version()}")
except Exception as e:
    print(f"   ❌ SSL connection failed: {e}")

# Test 5: Try sending a test SMS
print("\n5️⃣ Testing SMS API...")
print(f"   Username: {settings.AFRICASTALKING_USERNAME}")
print(f"   API Key: {'*' * 20}{settings.AFRICASTALKING_API_KEY[-4:]}")

try:
    # Try to send to a single test number
    test_number = "+254712345678"  # Replace with your number
    response = sms.send("Test from FlowMarket", [test_number])
    print(f"   ✅ API call successful!")
    print(f"   Response: {response}")
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
