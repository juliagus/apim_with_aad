# CALL APIM endpoint with token from Azure AD

from dotenv import load_dotenv
import os 
import requests
import json
import msal
import jwt
from datetime import datetime

load_dotenv(dotenv_path='.env.apim')

# for auth
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = [os.getenv("scope")] # Example scope for Microsoft Graph

def decode_jwt(token):
    """Decode JWT token and print the payload using PyJWT"""
    try:
        # Decode header without verification
        header_data = jwt.get_unverified_header(token)
        
        # Decode payload without verification (since we don't have the secret key)
        payload_data = jwt.decode(token, options={"verify_signature": False})
        
        print("=== JWT HEADER ===")
        print(json.dumps(header_data, indent=2))
        
        print("\n=== JWT PAYLOAD ===")
        print(json.dumps(payload_data, indent=2))
        
        # Convert timestamps to readable format
        print("\n=== DECODED TIMESTAMPS ===")
        if 'iat' in payload_data:
            iat = datetime.fromtimestamp(payload_data['iat'])
            print(f"Issued At (iat): {iat}")
        
        if 'nbf' in payload_data:
            nbf = datetime.fromtimestamp(payload_data['nbf'])
            print(f"Not Before (nbf): {nbf}")
            
        if 'exp' in payload_data:
            exp = datetime.fromtimestamp(payload_data['exp'])
            print(f"Expires At (exp): {exp}")
            
            # Check if token is expired
            now = datetime.now()
            if exp > now:
                time_left = exp - now
                print(f"Token is valid for: {time_left}")
            else:
                print("Token is EXPIRED")
                
    except Exception as e:
        print(f"Error decoding JWT: {e}")

def get_access_token():

    # --- MSAL Confidential Client Application Initialization ---
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
        )

    # --- Acquire Token ---
    try:
        result = app.acquire_token_for_client(scopes=SCOPE)
        print(result)

        if "access_token" in result:
            access_token = result["access_token"]
            print("Access Token acquired successfully.")
            # Decode and print the JWT token
            print("\n--- DECODING JWT TOKEN ---")
            decode_jwt(access_token)
            print("--- END JWT DECODING ---\n")
            
        else:
            print("Failed to acquire token.")
            print(f"Error: {result.get('error')}")
            print(f"Error Description: {result.get('error_description')}")

        return access_token

    except Exception as e:
        print(f"An error occurred: {e}")

def call_apim_endpoint(jwt_token):
    """ Call APIM endpoint for foundry model
    """

    subscription_key = os.getenv("APIM_SUBSCRIPTION_KEY") # apim subscription key
    api_version = "2024-05-01-preview"

    # apim base url " ex: https://apim-003.azure-api.net/<apiname>/models"
    api_base_url = os.getenv("API_BASE_URL") 
    endpoint = f"{api_base_url}/chat/completions?api-version={api_version}"

    model_name = "DeepSeek-R1"

    msg = {"model":model_name,
        "messages":[{"role":"system","content":"You are a helpful assistant"},
                    {"role":"user","content":"How are you?"}],
            "max_tokens":2048}
    
    headers = {
        "Content-Type": "application/json",
        "api-key": subscription_key,
        "Authorization": f"Bearer {jwt_token}"
    }

    rr = requests.post(url=endpoint, data=json.dumps(msg), headers=headers)
    print(rr.status_code)
    print(rr.text)

if __name__ == "__main__":
    token = get_access_token()
    if token:
        call_apim_endpoint(token)
    else:
        print("No token available to call the API.")