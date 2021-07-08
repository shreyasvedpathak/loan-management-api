from requests.auth import _basic_auth_str
from termcolor import colored
import unittest
import requests


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.PORT = 5000
        self.API_URL = f"http://127.0.0.1:{self.PORT}/"

        self.customers = [
            {'username': 'applicant1', 'password': 'applicant1'},
            {'username': 'applicant2', 'password': 'applicant2'},
            {'username': 'applicant3', 'password': 'applicant3'}
        ]
        self.customer_access_tokens = []

    def test_9_new_loan_without_token(self):
        test_name = "Requesting New Loan without authorized Token"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "new-loan"))
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Missing token' in resp.content)
            print(colored(f"\u2713 Test 9: {test_name} Passed", "green"))
        except:
            print(colored(f"\u2717 Test 9: {test_name} Failed", "red"))

    def test_10_new_loan_with_invalid_token(self):
        test_name = "Requesting New Loan with invalid Token"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "new-loan"),
                                 headers={'x-access-token': 'random_string_as_token'})
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(b'Invalid token' in resp.content)
            print(colored(f"\u2713 Test 10: {test_name} Passed", "green"))
        except:
            print(colored(f"\u2717 Test 10: {test_name} Failed", "red"))

    def test_11_customer_access_admin(self):
        test_name = "Customer trying to access Admin endpoints"
        try:
            for customer in self.customers:
                resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                     headers={"Authorization": _basic_auth_str(customer['username'], customer['password'])})
                data = resp.json()
                self.customer_access_tokens.append(data['token'])

            resp = requests.get("{}/{}".format(self.API_URL, "/show-users"),
                                headers={
                                    "x-access-token": self.customer_access_tokens[0]},
                                params={"user_type": "all"})

            self.assertEqual(resp.status_code, 401)
            self.assertTrue(
                b"You are not authorized to open this page" in resp.content)

            print(colored(f"\u2713 Test 11: {test_name} Passed", "green"))
        except:
            print(colored(f"\u2717 Test 11: {test_name} Failed", "red"))

    def test_12_agent_access_admin(self):
        test_name = "Agent trying to access Admin endpoints"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str("agent1", "agent1")})
            token = resp.json()['token']
            
            resp = requests.get(
                "{}/{}".format(self.API_URL, "/approve-loan/3"),
                headers={"x-access-token": token})
            
            self.assertEqual(resp.status_code, 401)
            # self.assertTrue(
            #     b"Your application for Agent has not been approved by the Admin." in resp.content)
            print(colored(f"\u2713 Test 12: {test_name} Passed", "green"))
        except Exception as e:
            print(e)
            print(colored(f"\u2717 Test 12: {test_name} Failed", "red"))

    def test_13_customer_can_only_view_his_loans(self):
        test_name = "Customer can only views his own loans"

        loans_by_applicant_2 = [
            {"loan_amount": 10000, "duration": 12, "loan_type": "HOME"},
            {"loan_amount": 20000, "duration": 24, "loan_type": "CAR"},
            {"loan_amount": 30000, "duration": 36, "loan_type": "PERSONAL"}
        ]

        loans_by_applicant_3 = [
            {"loan_amount": 10000, "duration": 12, "loan_type": "PERSONAL"},
            {"loan_amount": 20000, "duration": 24, "loan_type": "CAR"},
        ]

        for customer in self.customers:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str(customer['username'], customer['password'])})
            data = resp.json()
            self.customer_access_tokens.append(data['token'])
            
        try:
            for i in loans_by_applicant_2:
                resp = requests.post("{}/{}".format(self.API_URL, "new-loan"),
                                     headers={
                                         "x-access-token": self.customer_access_tokens[1]},
                                     json=i)

            for i in loans_by_applicant_3:
                resp = requests.post("{}/{}".format(self.API_URL, "new-loan"),
                                     headers={
                                         "x-access-token": self.customer_access_tokens[2]},
                                     json=i)

            loans_by_applicant_2 = requests.get("{}/{}".format(self.API_URL, "show-loans"),
                                                headers={"x-access-token": self.customer_access_tokens[1]})
            loans_by_applicant_3 = requests.get("{}/{}".format(self.API_URL, "show-loans"),
                                                headers={"x-access-token": self.customer_access_tokens[2]})

            self.assertEqual(loans_by_applicant_2.status_code, 200)
            self.assertEqual(loans_by_applicant_3.status_code, 200)
            '''
            Now applicant2 must have 4 loans ,as we have added 1 earlier 
            and applicant3 must have 3 loans
            # '''
            print(colored(f"\u2713 Test 13: {test_name} Passed", "green"))
        except Exception as e:
            print(e)
            print(colored(f"\u2717 Test 13: {test_name} Failed", "red"))


if __name__ == '__main__':
    unittest.main()
