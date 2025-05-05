import requests
import sys
import json

def test_rgb_values(color_code):
    """Test if RGB values are included in the API response for a color code"""
    url = f"http://localhost:8000/api/search/{color_code}"
    print(f"Testing API at {url}")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} formulations for color code '{color_code}'")
            
            rgb_count = 0
            for i, formulation in enumerate(data):
                print(f"\nFormulation {i+1}:")
                print(f"  Color code: {formulation.get('color_code')}")
                print(f"  Color card: {formulation.get('color_card')}")
                
                if 'color_rgb' in formulation:
                    rgb_count += 1
                    rgb = formulation['color_rgb']
                    print(f"  ✅ RGB values found: R:{rgb['rgb']['r']} G:{rgb['rgb']['g']} B:{rgb['rgb']['b']}")
                    print(f"  ✅ Hex value: {rgb['hex']}")
                else:
                    print(f"  ❌ No RGB values found for color card: {formulation.get('color_card')}")
            
            if rgb_count == 0:
                print(f"\n❌ No RGB values found for any formulation!")
                print("\nPossible reasons:")
                print("  1. The color_rgb_values table doesn't have an entry for this color code")
                print("  2. The color_card values don't match between formulations and color_rgb_values tables")
                print("  3. There might be an error in the API implementation")
            else:
                print(f"\n✅ Found RGB values for {rgb_count} out of {len(data)} formulations")
        elif response.status_code == 404:
            print(f"❌ Color code '{color_code}' not found")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Is your API server running at http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_rgb_values(sys.argv[1])
    else:
        print("Please provide a color code to test")
        print("Usage: python test_rgb.py <color_code>")
