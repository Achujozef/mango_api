import requests

def send_otp(phone_number, otp):
    """
    Sends an OTP to the specified phone number using the Fast2SMS API.
    """
    url = "https://www.fast2sms.com/dev/bulkV2"
    api_key = "AZJpgtyyjwckivy4bd7ZbZdxff9dumKS7p2osjXu5ctZqUNPNMQeOrlcjq4n"  
    payload = {
        "variables_values": otp,
        "route": "otp",
        "numbers": phone_number,
    }

    headers = {
        "authorization": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }

    try:
            response = requests.post(url, data=payload, headers=headers)
            
            print(f"Request URL: {url}")
            print(f"Payload: {payload}")
            print(f"Headers: {headers}")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            if response.status_code == 200:
                data = response.json()
                if data.get("return", False):
                    print("OTP sent successfully.")
                    return {"status": "success", "message": data.get("message", ["Message sent successfully"])}
                else:
                    print("Failed to send OTP. Response message:", data.get("message", ["Unknown error"]))
                    return {"status": "failure", "message": data.get("message", ["Failed to send message"])}
            else:
                print("HTTP request failed with status code:", response.status_code)
                return {"status": "error", "message": f"HTTP Error {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        print("An error occurred during the HTTP request:", str(e))
        return {"status": "error", "message": f"RequestException: {str(e)}"}