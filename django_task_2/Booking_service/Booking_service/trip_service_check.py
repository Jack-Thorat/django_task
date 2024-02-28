import requests

def check_trip_service():
    trip_service_url = 'http://127.0.0.1:8000/trip_details/TP12345678'  # Replace with the actual URL of Trip service
    try:
        response = requests.get(trip_service_url)
        if response.status_code == 200:
            print("Trip service is reachable.")
        else:
            print(f"Trip service is not reachable. Status code: {response.status_code}")
    except requests.ConnectionError:
        print("Failed to connect to Trip service. Connection refused.")

# Check if the trip service is reachable
check_trip_service()
