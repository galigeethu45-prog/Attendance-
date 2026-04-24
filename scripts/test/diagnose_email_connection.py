#!/usr/bin/env python
"""
Detailed Email Server Connection Diagnostics
Tests multiple connection methods and ports
"""
import socket
import ssl
import sys

print("=" * 80)
print("EMAIL SERVER CONNECTION DIAGNOSTICS")
print("=" * 80)

# Email server details
EMAIL_HOST = "mail.arraafiinfotech.com"
PORTS_TO_TEST = [25, 465, 587, 2525]

print(f"\n🔍 Testing connection to: {EMAIL_HOST}")
print("-" * 80)

# Test 1: DNS Resolution
print("\n1️⃣  DNS Resolution Test")
try:
    ip_address = socket.gethostbyname(EMAIL_HOST)
    print(f"   ✓ DNS resolved: {EMAIL_HOST} → {ip_address}")
except socket.gaierror as e:
    print(f"   ✗ DNS resolution failed: {e}")
    print("   → Email server hostname cannot be resolved")
    print("   → Check if hostname is correct")
    sys.exit(1)

# Test 2: Port Connectivity
print("\n2️⃣  Port Connectivity Test")
successful_ports = []

for port in PORTS_TO_TEST:
    try:
        print(f"\n   Testing port {port}...", end=" ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((EMAIL_HOST, port))
        
        if result == 0:
            print(f"✓ OPEN")
            successful_ports.append(port)
            
            # Try to get banner
            try:
                if port == 465:
                    # SSL port - wrap socket
                    context = ssl.create_default_context()
                    with context.wrap_socket(sock, server_hostname=EMAIL_HOST) as ssock:
                        ssock.settimeout(5)
                        banner = ssock.recv(1024).decode('utf-8', errors='ignore').strip()
                        if banner:
                            print(f"      Banner: {banner[:100]}")
                else:
                    # Plain text port
                    sock.settimeout(5)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        print(f"      Banner: {banner[:100]}")
            except:
                pass
        else:
            print(f"✗ CLOSED (error: {result})")
            
        sock.close()
        
    except socket.timeout:
        print(f"✗ TIMEOUT")
    except Exception as e:
        print(f"✗ ERROR: {e}")

# Test 3: SSL/TLS Test
print("\n3️⃣  SSL/TLS Connection Test")

if 465 in successful_ports:
    print(f"\n   Testing SSL on port 465...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((EMAIL_HOST, 465), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=EMAIL_HOST) as ssock:
                print(f"   ✓ SSL connection successful")
                print(f"      Protocol: {ssock.version()}")
                cert = ssock.getpeercert()
                if cert:
                    print(f"      Certificate subject: {dict(x[0] for x in cert['subject'])}")
    except Exception as e:
        print(f"   ✗ SSL connection failed: {e}")

if 587 in successful_ports:
    print(f"\n   Testing STARTTLS on port 587...")
    try:
        with socket.create_connection((EMAIL_HOST, 587), timeout=10) as sock:
            sock.recv(1024)  # Get banner
            sock.send(b"EHLO test\r\n")
            sock.recv(1024)  # Get response
            sock.send(b"STARTTLS\r\n")
            response = sock.recv(1024)
            
            if b"220" in response:
                context = ssl.create_default_context()
                with context.wrap_socket(sock, server_hostname=EMAIL_HOST) as ssock:
                    print(f"   ✓ STARTTLS successful")
                    print(f"      Protocol: {ssock.version()}")
            else:
                print(f"   ✗ STARTTLS not supported")
    except Exception as e:
        print(f"   ✗ STARTTLS test failed: {e}")

# Summary and Recommendations
print("\n" + "=" * 80)
print("SUMMARY AND RECOMMENDATIONS")
print("=" * 80)

if successful_ports:
    print(f"\n✓ Found {len(successful_ports)} accessible port(s): {', '.join(map(str, successful_ports))}")
    
    print("\n📝 Recommended Configuration:")
    
    if 465 in successful_ports:
        print("\n   Option 1: Port 465 (SSL)")
        print("   -------------------------")
        print("   EMAIL_HOST=mail.arraafiinfotech.com")
        print("   EMAIL_PORT=465")
        print("   EMAIL_USE_SSL=True")
        print("   EMAIL_USE_TLS=False")
        
    if 587 in successful_ports:
        print("\n   Option 2: Port 587 (TLS/STARTTLS)")
        print("   ----------------------------------")
        print("   EMAIL_HOST=mail.arraafiinfotech.com")
        print("   EMAIL_PORT=587")
        print("   EMAIL_USE_SSL=False")
        print("   EMAIL_USE_TLS=True")
        
    if 25 in successful_ports:
        print("\n   Option 3: Port 25 (Plain/STARTTLS)")
        print("   -----------------------------------")
        print("   EMAIL_HOST=mail.arraafiinfotech.com")
        print("   EMAIL_PORT=25")
        print("   EMAIL_USE_SSL=False")
        print("   EMAIL_USE_TLS=False")
        print("   (Note: May require TLS, test both ways)")
        
else:
    print("\n❌ NO ACCESSIBLE PORTS FOUND")
    print("\nPossible Issues:")
    print("  1. Firewall blocking outgoing SMTP connections")
    print("  2. Email server is down or not accessible")
    print("  3. Network restrictions (corporate firewall, ISP blocking)")
    print("  4. Wrong email server hostname")
    
    print("\n🔧 Troubleshooting Steps:")
    print("  1. Check with IT/Network admin about firewall rules")
    print("  2. Try from different network (mobile hotspot)")
    print("  3. Verify email server hostname with email provider")
    print("  4. Use alternative SMTP (Gmail, Outlook)")
    
    print("\n📧 Alternative: Use Gmail SMTP")
    print("  EMAIL_HOST=smtp.gmail.com")
    print("  EMAIL_PORT=587")
    print("  EMAIL_USE_TLS=True")
    print("  EMAIL_HOST_USER=your-email@gmail.com")
    print("  EMAIL_HOST_PASSWORD=your-app-password")
    print("  (Requires Gmail App Password - see GMAIL_SMTP_SETUP.md)")

print("\n" + "=" * 80)
print()
