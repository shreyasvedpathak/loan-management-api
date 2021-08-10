# Loan Management Flask API

## Table of Contents

- [Introduction](#introduction)
- [Frameworks](#frameworks)
- [Features](#features)
  - [Code Features](#code-features)
  - [API Features](#api-features)
- [Folder Structure](#folder-structure)
- [Installing](#installing)
- [Test Cases](#test-cases)
  - [Database](#database)
  - [Unauthorised API calls](#unauthorised-api-calls)
  - [API Calls](#api-calls)
- [Working](#working)
- [Endpoints](#endpoints)
  - [Common](#common)
  - [Customer](#customer)
  - [Agent](#agent)
  - [Admin](#admin)

## Introduction

I created this Loan Management API as a part of internship hiring challenge.

## Frameworks

- Flask
- PyJWT
- sqlite
- SQLAlchemy
- unittest
- Docker

## Features

### Code Features

- **Blueprints:**
  - Blueprints help keep project categorised and easy to scale as per requirements.
  - Besides code organization, there’s another advantage to structuring a Flask application as a collection of independent components so that one can reuse these components even across different applications!
- **Token Authentication:** Token based authentication using PyJWT.
- **Hashed Passwords:** Passwords are hashed using using bcrypt library. 12 is the default value for setting up complexity of salting while hashing.
- **Timezone:** Inorder to maintain timezone consistency we use `datetime.timezone.utc` from `datetime` library as using `datetime.utcnow` it means it is timezone naive, so you can't use it with `datetime.astimezone`.
- **Configurations:** All the configurations that are need to run this application are stored in 2 different files (app/config.py and app/constants.py) according to their purpose as this will help us to customise the application without going through all the code.

### API Features

1. **List, view and edit users -**  this can only be done by **"agent"** and **"admin"** roles
2. **Create a loan request on behalf of the user -**  This can only be done by **"agent"** role. Inputs would be tenure selected (in months) and interest to be charged every month. Loan can have 3 states - "NEW", "REJECTED", "APPROVED".
3. **Approval of loan request -** This can only be done by an **"admin"** role.
4. **Edit a loan (but not after it has been approved) -**  This can be done only by **"agent"** role. But cannot be done if loan is in "Approved" state.
5. **Ability to list and view loans (approved) or loan requests based on the filter applied by "filter"-** select by date of creation, date of update, state of loan (NEW, REJECTED, APPROVED), etc. This action can be done by all : **"customer"**, **"agent"** and **"admin"** roles. HOWEVER - **"customer"** can only see his own loans...while **"agent"** and **"admin"** can see everyone's loans.

## Folder Structure

```bash
┬── README.md
│   run.py
│   setup_db.py
│
└───app
    │   config.py
    │   constants.py
    │   site.db
    │   utils.py
    │   __init__.py
    │
    ├───admin
    │       routes.py
    │       __init__.py
    │
    ├───agent
    │       routes.py
    │       __init__.py
    │
    ├───customer
    │       models.py
    │       routes.py
    │       __init__.py
    │
    ├───main
    │       models.py
    │       routes.py
    │       __init__.py
    │
    └───test_cases
            test_cases_for_api_calls.py
            test_cases_for_database.py
            test_cases_for_unathorised_endpoints.py
```

## Installing

As this application uses Docker and its container, you will need to install Docker first and then run the following lines.

```bash
docker-compose build
docker-compose up -d
docker-compose run app
```

## Test Cases

### 1. Database

These test cases check if database is properly created and whether data is getting inserted properly  

**NOTE**:

- These test cases insert dummy data which will be used for further test cases.
- Do not delete or modify data after running these test cases.
- Do not run these tests more than once, as you will face constraint errors as it will try to add same data again.  

### 2. Unauthorised API calls

These test cases check if any user is trying to make API calls without a valid token or if they make API calls to the endpoints they are not authorized to make

For example:

- Requesting New Loan without authorized Token.
- Customer trying to access Admin endpoints.

### 3. API Calls

These test cases check if appropriate response is getting sent from their corresponding endpoints

For example:

- Show Customer List
- Approve Loans - Admin Only

**Note:**

- These tests need to be done in the same order as shwon above because they are dependent on results/modification done by the previous test(s).
- To test again from scratch use the setup_db.py script (app/setup_db.py)

To start testing

```bash
docker-compose exec app python app/test_cases/test_cases_for_database.py
docker-compose exec app python app/test_cases/test_cases_for_unathorised_endpoints.py
docker-compose exec app python app/test_cases/test_cases_for_api_calls.py
```

To reset database and start from scratch

```bash
docker-compose exec app python setup_db.py
```

## Working

- Different users can have different roles. The three roles are "customer", "agent" and "admin"
- Any user has to first login to start making call to any endpoint.
- Logging in will assign a token to the current logged in user, and will be unique to the user.
- The validatiy of the token is 60 mins. Any user cannot login if the token is invalid i.e. past the given validatity duration or has a invalid token. The user will have to get a new token by logging in again.
- Inorder for a agent to perform any agent related operation, the agent has to be approved by the admin first. All agents are unapproved by default.
- A customer can:
  - Apply for a new loan(s).
  - View applied loan(s).

- A agent can:
  - View all customers list.
  - View all loan(s):
    - Filter by loan status ("NEW", "APPROVED", "REJECTED")
    - Filter by loan creation or modified time.
  - View loan logbook.
  - Forward a loan request on behalf of the customer to the admin (Only for approved agents)
  - Edit the loan (Only before it is approved and not after)
  - View all loan requests.

- A admin can:
  - View all users (customers, agents)
  - View all loan requests made by a agent.
  - Approve loans.
  - Reject loans.
  - Register agents.
  - Approve agent applications.
  - View all approved as well as unapproved agent application.
  - View all loan(s):
    - Filter by loan status ("NEW", "APPROVED", "REJECTED")
    - Filter by loan creation or modified time.
  - View loan logbook.

## Endpoints

1. [Common](#common)
2. [Customer](#customer)
3. [Agent](#agent)
4. [Admin](#admin)

### Common

**POST**:

```python
/login

data = {
  "username": "<your username>",
  "password": "<your password>"
}
```

**GET**:

View loan history

```python
/view-loan-history/<loan_id>
```

Show customers

```python
/show-customers
```

Show loans

```json
/show-loans

Query Parameters:
    status : 
        all      - shows all loans   
        new      - shows all new loans    
        approved - shows all approved loans   
        rejected - shows all rejected loans   
        
    filter_type : 
        all      - shows all loans
        updated  - shows all updated loans
        
    start   : shows all the dates from the passed date (Format: YYYY-MM-DD)
    end     : shows all the dates till the passed date (Format: YYYY-MM-DD) 
```

### Customer

**POST**:

Register customer

```python
/register-customer

data = {
"username" : "your username",
"password" : "your password",
"email" : "your email",
"contact": "your contact"
}
```

Create a new loan

```python
/new-loan

data = {
"loan_amount" : "loan amount in numbers",
"loan_type" : "loan type",
"duration" : "duration in months"
}
```

### Agent

**POST**:

Edit a loan

```python
/edit-loan/<loan_id>

data = {
"loan_amount" : "loan amount in numbers",
"loan_type" : "loan type",
"duration" : "duration in months"
}
```

**GET**:

Request a loan approval from admin

```python
/request-loan/<loan_id>
```

Show all loan requests by an agent

```python
/loan-requests-by-agent
```

### Admin

**POST**:

```python
/register-agent

data = {
"username" : "your username",
"password" : "your password",
"email" : "your email",
"contact": "your contact"
}
```

**GET**:

Approve agent

```python
/approve-agent/<agent_id>
```

Show users

```json
/show-users

Query Parameters:
    status : 
        all      - shows all users (default)
        agents   - shows all agents
        customer - shows all customers
```

Show agent applications

```json
/show-agent-applications

Query Parameters:
    status:
        all        - shows all applications (default)
        approved   - shows all approved applications
        unapproved - shows all unapproved applications

```

Approve a loan

```python
/approve-loan/<loan_id>
```

Reject a loan

```python
/reject-loan/<loan_id>
```

Show all loan requests by a particular agent

```python
/agent-loan-requests/<agent_id>
```
