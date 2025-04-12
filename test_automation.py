import requests
import time
import sys
import os
import json
from typing import Optional, List
from datetime import datetime

class TestAutomation:
    # We Are currently using the LambdaTest API to automate the process of generating test code for web and mobile applications.
    # The class handles the entire process, including logging, error handling, and status updates.
    # It uses the requests library to interact with the LambdaTest API and Flask for logging.
    # The class is designed to be run in a standalone script, taking input from the command line or a JSON file.
    # The input should include an authentication token and a list of test IDs to process.
    # The class provides methods to get test details, generate test code, check test status, and process all tests. 


    # Give auth token it will Trigger from Details to Code Generation Status 
    def __init__(self, auth_token: str, test_ids: List[str]):
        self.base_url = "https://test-manager-api.lambdatest.com/api/atm/v1"
        self.headers = {
            "accept": "application/json",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": f"Bearer {auth_token}",
            "origin": "https://kaneai.lambdatest.com",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }
        self.test_ids = test_ids
        self.log_file = f"code_gen_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Initialize log file with header"""
        with open(self.log_file, 'w') as f:
            f.write(f"Code Generation Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")

    def _log_message(self, message: str):
        """Log message to file and print to console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        print(log_entry.strip())  # Print to console
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        # Send log to Flask app
        try:
            requests.post('http://localhost:5000/api/logs/update', json={
                'message': log_entry.strip(),
                'timestamp': timestamp
            })
        except:
            pass  # Ignore errors if Flask app is not running


    def get_test_details(self, test_id: str) -> Optional[str]:
        """Get test details and return test type"""
        url = f"{self.base_url}/test-details/{test_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            test_type = data.get("test_type")
            self._log_message(f"Test type for {test_id}: {test_type}")
            return test_type
        except requests.exceptions.RequestException as e:
            self._log_message(f"Error getting test details for {test_id}: {e}")
            return None

    def get_test_code(self, test_id: str, test_type: str) -> bool:
        """Get test code based on test type"""
        url = f"{self.base_url}/test/{test_id}/code"
        
        # Set parameters based on test type
        if test_type == "web":
            params = {
                "code_name": "Python-Selenium",
                "language": "python",
                "framework": "selenium",
                "folder_name": "",
                "accessibility": "false"
            }
        elif test_type == "mobile":
            params = {
                "code_name": "Python-Appium",
                "language": "python",
                "framework": "appium",
                "folder_name": "",
                "accessibility": "false"
            }
        else:
            self._log_message(f"Unsupported test type for {test_id}: {test_type}")
            return False

        try:
            self._log_message(f"Starting code generation for {test_id}...")
            response = requests.post(url, headers=self.headers, json=params)
            response.raise_for_status()
            self._log_message(f"Code generation started for {test_id}")
            return True
        except requests.exceptions.RequestException as e:
            self._log_message(f"Error getting test code for {test_id}: {e}")
            return False

    def check_test_status(self, test_id: str) -> Optional[str]:
        """Check test status and return success/failed"""
        url = f"{self.base_url}/test/{test_id}/codes"
        params = {
            "page": 1,
            "per_page": 10,
            "filter[code_name]": "",
            "sort_by": "committed_at"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract status from the nested data array
            status = None
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                # Get the first item from the data array
                first_item = data["data"][0]
                status = first_item.get("status")
            
            # Log the current status
            if status:
                self._log_message(f"Current codegen status for {test_id}: {status}")
                # Send status update to Flask app
                try:
                    requests.post('http://localhost:5000/api/status/update', json={
                        'test_id': test_id,
                        'status': status
                    })
                except:
                    pass  # Ignore errors if Flask app is not running
            else:
                self._log_message(f"Current codegen status for {test_id}: pending")
            
            return status
        except requests.exceptions.RequestException as e:
            self._log_message(f"Error checking test status for {test_id}: {e}")
            return None

    def process_test(self, test_id: str) -> bool:
        """Process a single test ID through all steps"""
        self._log_message(f"Starting processing for test ID: {test_id}")
        
        # Step 1: Get test details
        test_type = self.get_test_details(test_id)
        if not test_type:
            return False

        # Step 2: Get test code
        if not self.get_test_code(test_id, test_type):
            return False

        # Step 3: Poll for status
        self._log_message(f"Waiting for test completion for {test_id}...")
        max_attempts = 60  # 15 minutes maximum wait time
        attempt = 0
        
        while attempt < max_attempts:
            status = self.check_test_status(test_id)
            if status == "success":
                self._log_message(f"Code generation completed successfully for {test_id}")
                return True
            elif status == "failed":
                self._log_message(f"Code generation failed for {test_id}")
                return False
            elif status is None:
                self._log_message(f"Status check returned None for {test_id}, retrying...")
            
            attempt += 1
            time.sleep(15)
        
        self._log_message(f"Maximum wait time exceeded for {test_id}")
        return False

    def process_all_tests(self):
        """Process all test IDs and return results"""
        results = []
        for test_id in self.test_ids:
            self._log_message(f"\nProcessing test ID: {test_id}")
            success = self.process_test(test_id)
            results.append({
                "test_id": test_id,
                "status": "success" if success else "failed"
            })
            if success:
                self._log_message(f"Successfully completed processing for {test_id}")
            else:
                self._log_message(f"Failed to process test ID: {test_id}")
            self._log_message("Moving to next test ID...")
        
        return {
            "results": results,
            "log_file": self.log_file
        }

def main():
    # Get input from frontend
    try:
        input_data = json.loads(sys.stdin.read())
        auth_token = input_data.get('auth_token')
        test_ids = input_data.get('test_ids', [])
        
        if not auth_token or not test_ids:
            print(json.dumps({
                "error": "Missing required parameters",
                "details": "Both auth_token and test_ids are required"
            }))
            sys.exit(1)

        automation = TestAutomation(auth_token, test_ids)
        results = automation.process_all_tests()
        
        # Return results to frontend
        print(json.dumps(results))
        
    except json.JSONDecodeError:
        print(json.dumps({
            "error": "Invalid input format",
            "details": "Input must be valid JSON"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": "Unexpected error",
            "details": str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    main() 