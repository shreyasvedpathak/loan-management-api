from termcolor import colored
from requests.auth import _basic_auth_str
import unittest
import requests


class PopulateTests(unittest.TestCase):
    PORT = 5000
    API_URL = f"http://127.0.0.1:{PORT}/"

    admin_token = None
    customer_tokens = []
    agent_ids = []
    new_loans_ids = []

    def test_1_Admin_login(self):
        test_name = "Admin Login"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str("admin", "admin")})

            self.admin_token = resp.json()['token']

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(b'token' in resp.content)
            print(colored(f"\u2713 Test 1: {test_name} Passed", "green"))
        except Exception as e:
            print(colored("\u2717 Test 1: {test_name} Passed", "red"))
            print(e)

    def test_2_register_customer(self):
        test_name = "Customer Registration"
        customers = [
            {'username': 'applicant1', 'password': 'applicant1',
                'email': 'applicant1@gmail.com', 'contact': 'applicant1'},
            {'username': 'applicant2', 'password': 'applicant2',
             'email': 'applicant2@gmail.com', 'contact': 'applicant2'},
            {'username': 'applicant3', 'password': 'applicant3',
             'email': 'applicant3@gmail.com', 'contact': 'applicant3'}
        ]

        try:
            for customer in customers:
                resp = requests.post(
                    "{}/{}".format(self.API_URL, "register-customer"),
                    json=customer)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 1)

            print(colored(f"\u2713 Test 2: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 2: {test_name} Failed", "red"))
            print(e)

    def test_3_register_agent(self):
        test_name = "Agent Registration"
        agents = [{'username': 'agent1', 'password': 'agent1',
                   'email': 'agent1@gmail.com', 'contact': 'agent1'},
                  {'username': 'agent2', 'password': 'agent2',
                   'email': 'agent2@gmail.com', 'contact': 'agent2'}]

        try:
            for agent in agents:
                resp = requests.post(
                    "{}/{}".format(self.API_URL, "register-agent"),
                    json=agent)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 1)

            print(colored(f"\u2713 Test 3: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2717 Test 3: {test_name} Failed", "red"))
            print(e)

    def test_4_login_user(self):
        test_name = "Logging in Users"
        login_user_details = [{'username': 'applicant1', 'password': 'applicant1'},
                              {'username': 'applicant2', 'password': 'applicant2'},
                              {'username': 'applicant3', 'password': 'applicant3'}]
        try:
            for login_user in login_user_details:
                resp = requests.post("{}/{}".format(self.API_URL, "login"), headers={
                                     "Authorization": _basic_auth_str(login_user['username'],
                                                                      login_user['password'])},)
                data = resp.json()

                self.customer_tokens.append(data['token'])

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 2)
            print(colored(f"\u2713 Test 4: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2713 Test 4: {test_name} Failed", "red"))
            print(e)

    def test_5_new_loan(self):
        test_name = "Creating New Loans"
        
        loan_details = [{"loan_amount": 100000, "duration": 12, "loan_type": "HOME"},
                        {"loan_amount": 200000, "duration": 24, "loan_type": "CAR"},
                        {"loan_amount": 300000, "duration": 36, "loan_type": "PERSONAL"}]
        try:
            for loan, customer_token in zip(loan_details, self.customer_tokens):
                resp = requests.post("{}/{}".format(self.API_URL, "new-loan"), headers={
                                     "x-access-token": customer_token},
                                     json=loan)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()), 2)
            print(colored(f"\u2713 Test 5: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2713 Test 5: {test_name} Failed", "red"))
            print(e)

    def test_6_agent_login_without_admin_approval(self):
        '''
        Test should no login the agent as the agent isn't approved the admin.
        Unlsess and until admin doesn't approve agent , agent can no longer perform any operations
        '''

        test_name = "Logging in Agent without Admin's Approval"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str("agent1", "agent1")})

            self.assertEqual(resp.status_code, 401)
            self.assertTrue(
                b'Your application for Agent has not been approved by the Admin.' in resp.content)
            print(colored(f"\u2713 Test 6: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2713 Test 6: {test_name} Failed", "red"))
            print(e)

    def test_7_show_agent_applications(self):
        test_name = "Show Unapproved Agent Application"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str("admin", "admin")})

            self.admin_token = resp.json()['token']

            resp = requests.get("{}/{}".format(self.API_URL, "show-agent-applications"),
                                headers={"x-access-token": self.admin_token},
                                params={"status": "unapproved"})

            self.assertEqual(resp.status_code, 200)
            for agent in resp.json()["unapproved_agents"]:
                self.agent_ids.append(agent['id'])
            self.assertTrue(b'unapproved_agents' in resp.content)

            print(colored(f"\u2713 Test 7: {test_name} Passed", "green"))
        except Exception as e:
            print(colored(f"\u2713 Test 7: {test_name} Failed", "red"))
            print(e)

    def test_8_approve_agent_application(self):
        '''
        Approving agents from agent id which was previously unapproved
        '''
        test_name = "Approve Agent Applications by Agent ID"
        try:
            resp = requests.post("{}/{}".format(self.API_URL, "login"),
                                 headers={"Authorization": _basic_auth_str("admin", "admin")})

            self.admin_token = resp.json()['token']

            for agent_id in self.agent_ids:
                resp = requests.get(f"{self.API_URL}/approve-agent/{agent_id}",
                                    headers={"x-access-token": self.admin_token})

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(b'Message' in resp.content)
            print(colored(f"\u2713 Test 8: {test_name} Passed", "green"))
        except Exception as e:
            print(e)
            print(colored(f"\u2713 Test 8: {test_name} Failed", "red"))


if __name__ == '__main__':
    unittest.main()
