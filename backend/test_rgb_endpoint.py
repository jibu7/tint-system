import requests
import sys

def test_rgb_endpoint(color_code: str):
    """Test if the API endpoint returns RGB values correctly for a color code"""
    base_url = "http://localhost:8000"
    url = f"{base_url}/api/formulations/{color_code}"
    
    print(f"\nTesting endpoint: {url}")
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Found {len(data)} formulation(s) for color code '{color_code}'")
            
            for i, formulation in enumerate(data, 1):
                print(f"\nFormulation {i}:")
                print(f"  Color code: {formulation.get('color_code')}")
                print(f"  Color card: {formulation.get('color_card')}")
                
                if 'color_rgb' in formulation and formulation['color_rgb']:
                    rgb_data = formulation['color_rgb']
                    rgb = rgb_data.get('rgb', {})
                    hex_color = rgb_data.get('hex')
                    print(f"  ✅ RGB values found:")
                    print(f"    RGB: R:{rgb.get('r')} G:{rgb.get('g')} B:{rgb.get('b')}")
                    print(f"    HEX: {hex_color}")
                else:
                    print(f"  ❌ No RGB values found for color card: {formulation.get('color_card')}")
            
            rgb_count = sum(1 for f in data if f.get('color_rgb'))
            print(f"\nSummary:")
            print(f"✅ Found RGB values for {rgb_count} out of {len(data)} formulation(s)")
            
        elif response.status_code == 404:
            print(f"❌ Color code '{color_code}' not found")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Is the API server running at http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_rgb_endpoint(sys.argv[1])
    else:
        print("Please provide a color code to test")
        print("Usage: python test_rgb_endpoint.py <color_code>")
