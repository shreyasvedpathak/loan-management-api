# Internal imports
from app.utils import get_key, token_required
from app.constants import *
from app.main.models import Loan, Loan_Logbook
from app.customer.models import Users
from app.config import Config
from app import bcrypt

# External imports
from flask import jsonify, request, Blueprint, make_response
import jwt
import datetime

main = Blueprint('main', __name__)

@main.route("/login", methods=["POST"])
def login():
    auth = request.authorization

    if not auth.username or not auth.password:
        return make_response('Verification failed.', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    
    user = Users.query.filter_by(username=auth.username).first()
    
    if not user:
        return make_response('Verification failed.', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    
    if bcrypt.check_password_hash(user.password, auth.password):
        if user.role == ROLE['AGENT']:
            print(user.approved, user.email)
            if user.approved == False:
                return make_response('Your application for Agent has not been approved by the Admin.', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
        token = jwt.encode({'pub_id': user.pub_id, 
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, 
                           Config.SECRET_KEY)
        return jsonify({"token": token,
                        "Message": "Logged in successfully."})
        
    return make_response('Verification failed.', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})


@main.route("/view-loan-history/<loan_id>", methods=["GET"])
@token_required
def loan_history(current_user, loan_id):

    check_customer = Loan.query.filter_by(id=loan_id).first()
    
    if current_user.role == ROLE["CUSTOMER"] and current_user.id != check_customer.customer_id:
        return jsonify({"Message": "You are not authorised to see Loan objects except yours!"})
    
    query = Loan_Logbook.query.filter_by(
        loan_id=loan_id).order_by(Loan_Logbook.create_timestamp).all()
    
    response = {'Loan History': []}
    
    for i in query:
        response['Loan History'].append({
            "id": i.id,
            "Loan Type": get_key(i.loan_type, LOAN_TYPES),
            "Loan amount": i.loan_amount,
            "Duration": i.duration,
            "State": i.state,
            "Original loan id": i.loan_id,
            "Created At": i.create_timestamp
        })
    if(len(response['Loan History']) == 0):
        return jsonify({"Message": "No changes have been done on this loan object!"})
    return jsonify(response)


@main.route("/show-customers", methods=["GET"])
@token_required
def show_customers(current_user):
    if current_user.role == ROLE['CUSTOMER']:
        return jsonify({"Message": "You are not authorized to open this page."}), 401
    
    users = Users.query.filter_by(role=ROLE['CUSTOMER']).all()
    response = {'CUSTOMER': []}
    for user in users:
        response['CUSTOMER'].append({
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "pub_id": user.pub_id,
            "email": user.email,
            "contact": user.contact,
            "Created On": user.timestamp
        })
    if len(response['CUSTOMER']) == 0:
        return jsonify({"Message": "No customers in the database."})
    return jsonify(response)


@main.route("/show-loans", methods=["GET"])
@token_required
def show_loans(current_user):
    '''
    Parameters:
        status : 
            all      - shows all loans   
            new      - shows all new loans    
            approved - shows all approved loans   
            rejected - shows all rejected loans   
            
        filter_type : 
            all     - shows all loans
            updated - shows all updated loans
            
        start   : shows all the dates from the passed date (Format: YYYY-MM-DD)
        end     : shows all the dates till the passed date (Format: YYYY-MM-DD) 
    '''    
    status = request.args.get('status', 'all')
    filter_type = request.args.get('filter_type', 'all')
    start = request.args.get('start_date', '1985-01-17')
    end = request.args.get('end_date', '2025-09-17')
    
    query = Loan.query.filter(Loan.create_timestamp.between(start, end))
    
    if filter_type == 'updated':
        query = Loan.query.filter(Loan.update_timestamp.between(start, end))

    if current_user.role == ROLE["CUSTOMER"]:
        query = query.filter_by(customer_id = current_user.id)

    if status.upper() in ["NEW", "APPROVED", "REJECTED"]:
        query = query.filter_by(state=LOAN_STATUS[status.upper()])

    query = query.all()
    
    response = {'Loans': []}
    
    for loan in query:
        to_append = {
            "id": loan.id,
            "Loan Type": get_key(loan.loan_type, LOAN_TYPES),
            "Loan Amount": loan.loan_amount,
            "Rate of Interest": loan.roi,
            "Duration": loan.duration,
            "State": loan.state,
            "EMI": loan.emi,
            "Total Payable Amount": loan.total_payable_amount,
            "Created on" : loan.create_timestamp,
            "Updated on": loan.update_timestamp,
        }
        response['Loans'].append(to_append)

    if(len(response['Loans']) == 0):
        return jsonify({"Message": f"No {status} loans found between {start} - {end}"})
    return jsonify(response)
