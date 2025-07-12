import requests
import json
import os
from typing import List
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WHMManager:
    def __init__(self, username: str, api_token: str):
        self.whm_url = "https://host55.registrar-servers.com:2087"
        self.username = username
        self.api_token = api_token
        self.headers = {
            'Authorization': f'WHM {username}:{api_token}',
            'Content-Type': 'application/json'
        }

    def verify_connection(self) -> bool:
        """Verify connection to WHM and check if IP is whitelisted"""
        try:
            endpoint = f"{self.whm_url}/json-api/version"
            response = requests.get(endpoint, headers=self.headers, verify=False)
            if response.status_code == 200:
                print("✓ Successfully connected to WHM")
                print("✓ IP is whitelisted")
                return True
            else:
                print(f"✗ Connection failed: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False

    def list_accounts(self) -> List[dict]:
        """List all accounts on the server"""
        endpoint = f"{self.whm_url}/json-api/listaccts"
        response = requests.get(endpoint, headers=self.headers, verify=False)
        if response.status_code == 200:
            return response.json().get('data', {}).get('acct', [])
        else:
            raise Exception(f"Failed to list accounts: {response.text}")

    def delete_account(self, username: str) -> bool:
        """Delete a specific account"""
        endpoint = f"{self.whm_url}/json-api/removeacct"
        params = {
            'api.version': 1,
            'username': username
        }
        response = requests.get(endpoint, headers=self.headers, params=params, verify=False)
        return response.status_code == 200

    def is_wordpress_installation(self, account: dict) -> bool:
        """Check if an account has WordPress installed"""
        # This is a basic check - you might want to enhance this
        return 'wordpress' in account.get('domain', '').lower() or 'wp-' in account.get('domain', '').lower()

def main():
    print("WHM WordPress Account Manager")
    print("=============================")
    
    # Get credentials from environment variables or user input
    username = os.getenv('WHM_USERNAME') or input("Enter WHM username: ")
    api_token = os.getenv('WHM_API_TOKEN') or input("Enter WHM API token: ")

    whm = WHMManager(username, api_token)
    
    try:
        # Verify connection first
        if not whm.verify_connection():
            print("Please check your credentials and IP whitelist status")
            return
            
        # Get all accounts
        print("\nFetching accounts...")
        accounts = whm.list_accounts()
        print(f"\nFound {len(accounts)} accounts")
        
        # Filter WordPress accounts (excluding newageweb.it.com)
        wordpress_accounts = [
            acc for acc in accounts 
            if whm.is_wordpress_installation(acc) 
            and 'newageweb.it.com' not in acc.get('domain', '')
        ]
        
        if not wordpress_accounts:
            print("\nNo WordPress accounts found to delete")
            return
            
        print(f"\nFound {len(wordpress_accounts)} WordPress accounts to delete:")
        for i, acc in enumerate(wordpress_accounts, 1):
            print(f"{i}. {acc.get('user', '')} ({acc.get('domain', '')})")
        
        # Confirm deletion
        confirm = input("\nDo you want to proceed with deletion? (yes/no): ")
        if confirm.lower() == 'yes':
            print("\nStarting deletion process...")
            for acc in wordpress_accounts:
                username = acc.get('user', '')
                print(f"\nDeleting account: {username}")
                if whm.delete_account(username):
                    print(f"✓ Successfully deleted {username}")
                else:
                    print(f"✗ Failed to delete {username}")
            print("\nDeletion process completed")
        else:
            print("\nOperation cancelled")
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 