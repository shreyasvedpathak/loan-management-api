# Internal imports
from app import db
from app.constants import *
from app.main.models import Loan
from app.customer.models import Users
from app.utils import get_key, token_required

# External imports
from flask import request, jsonify, Blueprint

customer = Blueprint('customer', __name__)


@customer.route("/register-customer", methods=["POST"])
def register_Customer():

    data = request.get_json()

    new_user = Users(data["username"], data["email"],
                     data['contact'], data['password'])

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Message': 'Account successfully created.'})


@customer.route("/new-loan", methods=["POST"])
@token_required
def new_loan(current_user):

    data = request.get_json()

    if(data == None):
        return jsonify({'Message': 'No data was passed for applying loan.'}), 401

    new_loan = Loan(data["loan_amount"], data["duration"],
                    current_user.id, loan_type=LOAN_TYPES[data['loan_type']])
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({
        'Message': 'Your Loan Application has been successfully created. Waiting for approval.',
        "data": {
            "Loan amount": new_loan.loan_amount,
            "Duration": new_loan.duration,
            "Rate of Interest": new_loan.roi,
            "EMI": new_loan.emi,
            "Total amount to be paid": new_loan.total_payable_amount,
            "Loan Type": get_key(new_loan.loan_type, LOAN_TYPES),
            "Created on ": new_loan.create_timestamp
        }
    })
