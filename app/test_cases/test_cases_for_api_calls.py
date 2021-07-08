import unittest
import requests
from requests.auth import _basic_auth_str
from termcolor import colored


class ApiTests(unittest.TestCase):

    def setUp(self):
        self.PORT = 5000
        self.API_URL = f"http://127.0.0.1:{self.PORT}/"

        resp = requests.post("{}/{}".format(self.API_URL, "login"),
                             headers={"Authorization": _basic_auth_str("admin", "admin")})
        self.admin_access_token = (resp.json()['token'])

        resp = requests.post("{}/{}".format(self.API_URL, "login"),
                             headers={"Authorization": _basic_auth_str("agent1", "agent1")})
        self.agent_access_token = (resp.json()['token'])

        resp = requests.post("{}/{}".format(self.API_URL, "login"),
                             headers={"Authorization": _basic_auth_str("applicant1", "applicant1")})
        self.customer_access_token = (resp.json()['token'])

        try:
            self.loan_id = requests.get("{}/{}".format(self.API_URL, "show-loans?status=new"),
                                   headers={
                                   "x-access-token": self.agent_access_token}).json()['Loans'][0]['id']
        except Exception:
            self.loan_id = requests.get("{}/{}".format(self.API_URL, "show-loans?status=approved"),
                                   headers={
                                   "x-access-token": self.agent_access_token}).json()['Loans'][0]['id']

        self.previos_loan_id = self.loan_id

    def test_15_show_customers(self):
        test_name = "Show Customer List"
        try:
            resp = requests.get("{}/{}".format(self.API_URL, "show-customers"),
                                headers={"x-access-token": self.admin_access_token})
            self.assertEqual(resp.status_code, 200)
            resp = requests.get("{}/{}".format(self.API_URL, "show-customers"),
                                headers={"x-access-token": self.agent_access_token})
            self.assertEqual(resp.status_code, 200)
            resp = requests.get("{}/{}".format(self.API_URL, "show-customers"),
                                headers={"x-access-token": self.customer_access_token})
            self.assertEqual(resp.status_code, 401)
            print(colored(f"\u2713 Test 15: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 15: {test_name} Failed", "red"))

    def test_16_show_users(self):
        test_name = "Show all Users"
        try:
            resp = requests.get("{}/{}".format(self.API_URL, "show-users"),
                                headers={"x-access-token": self.admin_access_token})
            self.assertEqual(resp.status_code, 200)
            resp = requests.get("{}/{}".format(self.API_URL, "show-users"),
                                headers={"x-access-token": self.agent_access_token})
            self.assertEqual(resp.status_code, 401)
            resp = requests.get("{}/{}".format(self.API_URL, "show-users"),
                                headers={"x-access-token": self.customer_access_token})
            self.assertEqual(resp.status_code, 401)
            print(colored(f"\u2713 Test 16: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 16: {test_name} Failed", "red"))

    def test_17_loan_request(self):
        test_name = "Make Loan Request - Agent Only"
        try:
            resp = requests.get(f"{self.API_URL}/request-loan/{self.loan_id}",
                                headers={"x-access-token": self.admin_access_token})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Unauthorised Access' in resp.content)

            resp = requests.get(f"{self.API_URL}/request-loan/{self.loan_id}",
                                headers={"x-access-token": self.customer_access_token})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Unauthorised Access' in resp.content)

            resp = requests.get(f"{self.API_URL}/request-loan/{self.loan_id}",
                                headers={"x-access-token": self.agent_access_token})
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(
                b"Request has sent successfully. Wait for Admin's approval." in resp.content)

            print(colored(f"\u2713 Test 17: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 17: {test_name} Failed", "red"))
            print(e)

    def test_18_admin_approve_loan(self):
        test_name = "Approve Loan - Admin Only"
        try:
            resp = requests.get(f"{self.API_URL}/approve-loan/{self.loan_id}",
                                headers={"x-access-token": self.admin_access_token})

            resp = requests.get(f"{self.API_URL}/approve-loan/{self.loan_id}",
                                headers={"x-access-token": self.agent_access_token})
            self.assertEqual(resp.status_code, 401)

            resp = requests.get(f"{self.API_URL}/approve-loan/{self.loan_id}",
                                headers={"x-access-token": self.customer_access_token})
            self.assertEqual(resp.status_code, 401)

            self.previos_loan_id = self.loan_id
            try:
                self.loan_id = requests.get("{}/{}".format(self.API_URL, "show-loans?status=new"), headers={
                                            "x-access-token": self.agent_access_token}).json()['Loans'][0]['id']
            except Exception:
                self.loan_id = requests.get("{}/{}".format(self.API_URL, "show-loans?status=approved"), headers={
                                            "x-access-token": self.agent_access_token}).json()['Loans'][0]['id']
            print(colored(f"\u2713 Test 18: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 18: {test_name} Failed", "red"))

    def test_19_filter_loans(self):
        test_name = "Filter Loans by State"
        try:
            resp = requests.get("{}/{}".format(self.API_URL, "show-loans"),
                                headers={"x-access-token": self.admin_access_token}, 
                                params={'status': 'approved'})
            
            self.assertEqual(resp.status_code, 200)
            loan_status = resp.json()['Loans'][0]['State']
            self.assertEqual(loan_status, 0)

            resp = requests.get("{}/{}".format(self.API_URL, "show-loans"),
                                headers={"x-access-token": self.agent_access_token}, 
                                params={'status': 'approved'})
            self.assertEqual(resp.status_code, 200)
            loan_status = resp.json()['Loans'][0]['State']
            self.assertEqual(loan_status, 0)

            resp = requests.get("{}/{}".format(self.API_URL, "show-loans"),
                                headers={"x-access-token": self.agent_access_token}, 
                                params={'status': 'new'})
            self.assertEqual(resp.status_code, 200)
            loan_status = resp.json()['Loans'][0]['State']
            self.assertEqual(loan_status, 2)

            print(colored(f"\u2713 Test 19: {test_name} Passed", "green"))

        except Exception as e:
            print(e)
            print(colored(f"\u2717 Test 19: {test_name} Failed", "red"))

    def test_20_edit_loan(self):
        test_name = "Edit Loan - Only Agent"

        data = {
            'loan_amount': 15000,
            'duration': 6
        }
        
        try:
            resp = requests.post(f"{self.API_URL}/edit-loan/{self.loan_id}",
                                 headers={"x-access-token": self.admin_access_token}, 
                                 json=data)
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Unauthorised Access' in resp.content)

            resp = requests.post(f"{self.API_URL}/edit-loan/{self.loan_id}",
                                 headers={"x-access-token": self.agent_access_token}, 
                                 json=data)
            self.assertEqual(resp.status_code, 200)
            
            resp = requests.get(f"{self.API_URL}/approve-loan/{self.loan_id}",
                                headers={"x-access-token": self.admin_access_token})
            
            resp = requests.post(f"{self.API_URL}/edit-loan/{self.loan_id}",
                                 headers={"x-access-token": self.agent_access_token}, 
                                 json=data)
            
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(
                b'It cannot be changed now' in resp.content)
            
            print(colored(f"\u2713 Test 20: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 20: {test_name} Failed", "red"))
            print(e)


if __name__ == '__main__':
    unittest.main()
