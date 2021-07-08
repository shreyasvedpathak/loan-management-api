# Internal imports
from app.constants import *
from app import db
from app.main.models import Loan, Loan_Logbook
from app.utils import get_key, token_required

# External imports
from flask import request, jsonify, Blueprint
import datetime


agent = Blueprint('agent', __name__)


@agent.route("/request-loan/<loan_id>", methods=["GET"])
@token_required
def make_loan_request(current_user, loan_id):
    if(current_user.role == ROLE['AGENT']):
        try:
            loan = Loan.query.filter_by(id=loan_id).first()
        except Exception as ex:
            return jsonify({"Message": f"There is no loan with id: {loan_id}"}), 400
        loan.agent_id = current_user.id
        db.session.commit()
        return jsonify({"Message": "Request has sent successfully. Wait for Admin's approval."})
    else:
        return jsonify({"Message": "Unauthorised Access"}), 401


@agent.route("/loan-requests-by-agent", methods=["GET"])
@token_required
def get_requests(current_user):
    if(current_user.role == ROLE['AGENT']):
        loans = Loan.query.filter_by(agent_id=current_user.id)
        response = {"Loan Requests": []}
        if loans:
            for loan in loans:
                response["Loan Requests"].append({
                    "id": loan.id,
                    "Loan Amount": loan.loan_amount,
                    "Loan Type": get_key(loan.loan_type, LOAN_TYPES),
                    "Rate of Interest": loan.roi,
                    "Duration": loan.duration,
                    "EMI": loan.emi,
                    "status": get_key(loan.state, LOAN_STATUS),
                    "Total Payable Amount": loan.total_payable_amount,
                    "Customer Id": loan.customer_id,
                    "Agent Id": loan.agent_id,
                    "Created On": loan.create_timestamp,
                    "Updated On": loan.update_timestamp
                })
        if len(response["Loan Requests"]) == 0:
            return jsonify({"Message": "No requests."})
        return jsonify(response)
    else:
        return jsonify({"Message": "Not authorized to view this page."}), 401


@agent.route("/edit-loan/<loan_id>", methods=["POST"])
@token_required
def edit_loan(current_user, loan_id):
    

    if(current_user.role != ROLE['AGENT']):
        return jsonify({"Message": "Unauthorised Access"}), 401

    data = request.get_json()

    try:
        loan = Loan.query.filter_by(id=loan_id).first()
    except Exception:
        return jsonify({"Message": f"There is no loan with id: {loan_id}"}), 400

    if(get_key(loan.state, LOAN_STATUS) == "APPROVED"):
        return jsonify({"Message": f"Loan id: {loan_id}, has already approved. It cannot be changed now."}), 200

    previous_loan = Loan_Logbook(loan_id=int(loan_id), loan_type=loan.loan_type,
                                 loan_amount=loan.loan_amount, duration=loan.duration, 
                                 state=loan.state)

    db.session.add(previous_loan)
    db.session.commit()

    if data == None:
        return jsonify({'Message': 'No data was passed for loan modification. Try again.'}), 401

    try:
        loan.loan_amount = data["loan_amount"]
        loan.last_updated_by = current_user.id
        loan.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass

    try:
        loan.loan_type = LOAN_TYPES[data["loan_type"]]
        loan.last_updated_by = current_user.id
        loan.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass

    try:
        loan.duration = data["duration"]
        loan.last_updated_by = current_user.id
        loan.update_timestamp = datetime.datetime.now(datetime.timezone.utc)
    except KeyError:
        pass

    db.session.commit()

    return jsonify({'Message': 'Your Loan Application has been successfully Modified',
                    "Loan information":
                    {
                        "Loan amount": loan.loan_amount,
                        "Duration": loan.duration,
                        "Rate of Interest": loan.roi,
                        "EMI": loan.emi,
                        "Total amount to be paid": loan.total_payable_amount,
                        "Loan Type": get_key(loan.loan_type, LOAN_TYPES),
                        "Updated on ": loan.update_timestamp
                    }
                    })