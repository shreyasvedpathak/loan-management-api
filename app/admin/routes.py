# Internal imports
from app.constants import *
from app import db
from app.customer.models import Users
from app.main.models import Loan
from app.utils import get_key, token_required

# External imports
from flask import request, jsonify, Blueprint

admin = Blueprint('admin', __name__)


@admin.route("/register-agent", methods=["POST"])
def register_Agent():
    '''
    register_Agent : To register a new Agent.
    '''
    data = request.get_json()

    new_user = Users(data["username"], data["email"], data['contact'],
                     data['password'], role=ROLE['AGENT'], approved=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"Message": "Your request has been sent successfully"})


@admin.route("/approve-agent/<agent_id>", methods=["GET"])
@token_required
def approve_agent(current_user, agent_id):

    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."})

    agent = Users.query.filter_by(id=agent_id).first()

    if(agent.approved == True):
        return jsonify({"Message": "Already approved."})
    agent.approved = True
    db.session.commit()
    return jsonify({"Message": "This agent has been approved."})


@admin.route("/show-users", methods=["GET"])
@token_required
def show_user(current_user):
    """
    Parameters:
    status : 
        all      - shows all users
        agents   - shows all agents
        customer - shows all customers
    """
    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."}), 401

    user_type = request.args.get("user_type", "all")

    if user_type not in ["all", "agents", "customer", None]:
        return jsonify({"Message": "Wrong request. Please check the endpoints."}), 401

    if user_type == "agents":
        users = Users.query.filter_by(role=ROLE['AGENT']).all()
    elif user_type == "customer":
        users = Users.query.filter_by(role=ROLE['CUSTOMER']).all()
    else:
        users = Users.query.all()

    response = {'Users': []}
    for user in users:
        response['Users'].append({
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "pub_id": user.pub_id,
            "email": user.email,
            "contact": user.contact,
            "Created On": user.timestamp
        })
    if len(response['Users']) == 0:
        return jsonify({"Message": "No users in the database."})
    return jsonify(response)


@admin.route("/show-agent-applications", methods=["GET"])
@token_required
def get_agents_requests(current_user):
    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."})

    status = request.args.get("status", "all")

    if status not in ["all", "approved", "unapproved", None]:
        return jsonify({"Message": "Wrong request. Please check the endpoints."}), 401

    if status == "approved":
        agents = Users.query.filter_by(role=ROLE['AGENT'], approved=True).all()
    elif status == "unapproved":
        agents = Users.query.filter_by(
            role=ROLE['AGENT'], approved=False).all()
    else:
        agents = Users.query.filter_by(role=ROLE['AGENT']).all()

    response = {f"{status}_agents": []}

    for agent in agents:
        response[f"{status}_agents"].append({
            "id": agent.id,
            "username": agent.username,
            "password": agent.password,
            "pub_id": agent.pub_id,
            "email": agent.email,
            "contact": agent.contact,
            "Created On": agent.timestamp
        })
    if len(response[f"{status}_agents"]) == 0:
        return jsonify({"Message": "No pending agent applications  in the system!"})
    return jsonify(response), 200


@admin.route("/approve-loan/<loan_id>", methods=["GET"])
@token_required
def approve_loan(current_user, loan_id):
    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."}), 401

    try:
        loan = Loan.query.filter_by(id=loan_id).first()
    except Exception:
        return jsonify({"Message": f"There is no loan with id: {loan_id}"}), 400
    loan.state = LOAN_STATUS['APPROVED']
    db.session.commit()
    return jsonify({"Message": "The loan is successfully approved."})


@admin.route("/reject-loan/<loan_id>", methods=["GET"])
@token_required
def reject_loan(current_user, loan_id):
    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."})

    try:
        loan = Loan.query.filter_by(id=loan_id).first()
    except Exception:
        return jsonify({"Message": f"There is no loan with id: {loan_id}"}), 400

    loan.state = LOAN_STATUS['REJECTED']
    db.session.commit()
    return jsonify({"Message": "The loan has been successfully rejected."})


@admin.route("/agent-loan-requests/<agent_id>", methods=["GET"])
@token_required
def agent_loan(current_user, agent_id):

    if current_user.role in [ROLE['AGENT'], ROLE['CUSTOMER']]:
        return jsonify({"Message": "You are not authorized to open this page."})

    loans = Loan.query.filter_by(agent_id=agent_id)

    response = {"loan_requests": []}
    if loans:
        for loan in loans:
            response["loan_requests"]({
                "id": loan.id,
                "Loan Amount": loan.loan_amount,
                "Loan Type": get_key(loan.loan_type, LOAN_TYPES),
                "Rate of interest": loan.roi,
                "Duration": loan.duration,
                "EMI": loan.emi,
                "Status": get_key(loan.state, LOAN_STATUS),
                "Total Payable amount": loan.total_payable_amount,
                "Customer Id": loan.customer_id,
                "Agent Id": loan.agent_id,
                "Created On": loan.create_timestamp,
                "Updated On": loan.update_timestamp
            })
    if len(response["loan_requests"]) == 0:
        return jsonify({"Message": "No request for Loans from this particular agent found found !"})
    return jsonify(response)
