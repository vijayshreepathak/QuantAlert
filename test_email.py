# test_email.py
from app.email_service import test_email_connection, send_test_email
import asyncio

async def main():
    print("🧪 Testing QuantAlert Email Configuration")
    print("=" * 50)
    
    # Test 1: Connection Test
    print("\n1️⃣ Testing SMTP connection...")
    connection_ok = test_email_connection()
    
    if connection_ok:
        print("✅ SMTP connection successful!")
        
        # Test 2: Send actual test email
        print("\n2️⃣ Sending test email...")
        try:
            send_test_email("vijayshree.76676@gmail.com")  # Send to yourself
            print("✅ Test email sent successfully!")
        except Exception as e:
            print(f"❌ Test email failed: {e}")
    else:
        print("❌ SMTP connection failed - fix configuration first")

if __name__ == '__main__':
    asyncio.run(main())
