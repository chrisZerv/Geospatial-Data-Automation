import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Sentinel Hub Credentials
CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")
API_URL = "https://services.sentinel-hub.com/oauth/token"

# Area of Interest (Polygon Coordinates)
coordinates = {
    "type": "Polygon",
    "coordinates": [[
        [23.694077, 37.942031],
        [23.694077, 38.262985],
        [24.043579, 38.262985],
        [24.043579, 37.942031],
        [23.694077, 37.942031]
    ]]
}

# Time range
start_date = "2024-08-12"
end_date = "2024-08-12"

# Evalscript to get the SWIR composite
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B12", "B8A", "B04", "dataMask"],
    output: { bands: 4 }
  };
}

function evaluatePixel(sample) {
  return [2.5 * sample.B12, 2.5 * sample.B8A, 2.5 * sample.B04, sample.dataMask];
}
"""


# Request token from Sentinel Hub
def get_sentinel_token(client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(API_URL, data=payload)
    return response.json().get('access_token')


# Prepare Sentinel Hub request for SWIR Composite
def get_swir_image(token, aoi, start_date, end_date, evalscript):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "input": {
            "bounds": {
                "geometry": aoi
            },
            "data": [
                {
                    "type": "S2L2A",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{start_date}T00:00:00Z",
                            "to": f"{end_date}T23:59:59Z"
                        }
                    }
                }
            ]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        "evalscript": evalscript
    }

    # Post request to Sentinel Hub API
    process_url = "https://services.sentinel-hub.com/api/v1/process"
    response = requests.post(process_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# Save image to file
def save_image(image_data, file_name):
    with open(file_name, 'wb') as file:
        file.write(image_data)


# Main Program
def main():
    token = get_sentinel_token(CLIENT_ID, CLIENT_SECRET)

    if token:
        print("Token retrieved successfully.")

        # Get the SWIR composite image
        image_data = get_swir_image(token, coordinates, start_date, end_date, evalscript)

        if image_data:
            # Save the image locally
            save_image(image_data, "swir_composite.tiff")
            print("SWIR image saved successfully.")
        else:
            print("Failed to retrieve SWIR image.")
    else:
        print("Failed to get Sentinel Hub token.")


if __name__ == "__main__":
    main()
