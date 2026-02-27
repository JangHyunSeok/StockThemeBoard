"""
API Health Check Script
Tests if the backend API endpoints are accessible and functioning
"""
import sys
import socket

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("=" * 60)
    print("API Endpoint Health Check")
    print("=" * 60)
    
    # Check if port 3000 is open
    print("\n1. Checking if backend is running on port 3000...")
    if check_port('localhost', 3000):
        print("   ✅ Port 3000 is OPEN - Backend server is running")
    else:
        print("   ❌ Port 3000 is CLOSED - Backend server is NOT running")
        print("   Please start the backend with: docker-compose up -d")
        sys.exit(1)
    
    # Try to import requests
    try:
        import requests
    except ImportError:
        print("\n❌ 'requests' library not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # Test health endpoint
    print("\n2. Testing /health endpoint...")
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # Test root endpoint
    print("\n3. Testing / (root) endpoint...")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint OK: {data.get('message', 'N/A')}")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
    
    # Test volume-rank-by-theme endpoint
    print("\n4. Testing /api/v1/rankings/volume-rank-by-theme?market=KRX...")
    try:
        response = requests.get(
            "http://localhost:3000/api/v1/rankings/volume-rank-by-theme?market=KRX",
            timeout=30  # This endpoint may take longer
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print(f"   ✅ API is working!")
                print(f"   Number of themes returned: {len(data)}")
                if data:
                    first_theme = list(data.keys())[0]
                    print(f"   First theme: '{first_theme}' with {len(data[first_theme])} stocks")
            else:
                print(f"   ⚠️  Unexpected response format: {type(data)}")
        elif response.status_code == 503:
            print(f"   ❌ Service Unavailable (503)")
            print(f"   Error: {response.text[:200]}")
        else:
            print(f"   ❌ Error response")
            print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out (>30s)")
        print(f"   This may indicate the backend is still loading or experiencing issues")
    except Exception as e:
        print(f"   ❌ Request failed: {type(e).__name__}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
