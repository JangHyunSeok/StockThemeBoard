import requests
import json

try:
    print("Testing API endpoint...")
    response = requests.get("http://localhost:3000/api/v1/rankings/volume-rank-by-theme?market=KRX", timeout=10)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nHeaders: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API is working!")
        print(f"Number of themes: {len(data)}")
        print(f"Theme names: {list(data.keys())[:5]}...")  # First 5 themes
    else:
        print(f"\n❌ API returned error")
        print(f"Response text: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error - Backend server is not running or not accessible on port 3000")
except requests.exceptions.Timeout:
    print("\n❌ Timeout - Server took too long to respond")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
