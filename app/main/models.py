# Internal imports
from app import db
from app.constants import *

# External imports
import datetime

class Loan_Logbook(db.Model):
    """ Loan update model """
    __tablename__ = "Loan_Logbook"

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("Loans.id"))
    loan_type = db.Column(db.Integer,  nullable=False)
    loan_amount = db.Column(db.Float,  nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    create_timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, loan_id, loan_amount, duration, state=LOAN_STATUS['NEW'], loan_type=LOAN_TYPES['HOME']):
        self.loan_id = loan_id
        self.loan_type = loan_type
        self.loan_amount = loan_amount
        self.duration = duration
        self.state = state
        self.create_timestamp = datetime.datetime.now(datetime.timezone.utc)


class Loan(db.Model):
    """ Loan model """
    __tablename__ = "Loans"

    id = db.Column(db.Integer, primary_key=True)
    loan_type = db.Column(db.Integer,  nullable=False)
    loan_amount = db.Column(db.Float,  nullable=False)
    roi = db.Column(db.Float,  nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    emi = db.Column(db.Float, nullable=False)
    total_payable_amount = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Users.id"))
    agent_id = db.Column(db.Integer, default=None)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("Users.id"))
    create_timestamp = db.Column(db.DateTime, nullable=False)
    update_timestamp = db.Column(db.DateTime, nullable=False)


    def get_emi(self, loan_amount, loan_type, duration):
        '''get_emi Return EMI

        Args:
            loan_amount (float): Loan Amount
            loan_type (int): Loan Type
            duration (int): Months

        Returns:
            float: EMI
        '''        
        P = loan_amount
        r = ROI[loan_type] / (12 * 100)
        n = duration
        return (P * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    
    def get_total_payable(self, loan_amount, loan_type, duration):
        '''get_total_payable Return Total Payable Amount

        Args:
            loan_amount (float): Loan Amount
            loan_type (int): Loan Type
            duration (int): Months

        Returns:
            float: Total Payable Amount
        '''        
        P = loan_amount
        r = ROI[loan_type]
        n = duration / 12
        return P + (P * r * n) / 100
        
    
    def __init__(self, loan_amount, duration, customer_id, state=LOAN_STATUS['NEW'], loan_type=LOAN_TYPES['HOME']):
        self.loan_type = loan_type
        self.roi = ROI[loan_type]
        self.loan_amount = loan_amount
        self.duration = duration
        self.state = state
        self.emi = self.get_emi(loan_amount, loan_type, duration)
        self.total_payable_amount = self.get_total_payable(loan_amount, loan_type, duration)
        self.customer_id = customer_id
        self.last_updated_by = customer_id
        self.agent_id = (-1)
        self.create_timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.update_timestamp = datetime.datetime.now(datetime.timezone.utc)

