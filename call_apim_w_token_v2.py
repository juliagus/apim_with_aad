# CALL APIM endpoint with token from Azure AD

from dotenv import load_dotenv
import os 
import requests
import json
import msal

load_dotenv(dotenv_path='.env.apim')

# for auth
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = [os.getenv("scope")] # Example scope for Microsoft Graph

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
            # You can now use this access_token to call protected APIs
            #print(f"Access Token: {access_token}")
            
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