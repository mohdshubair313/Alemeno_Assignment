from celery import shared_task
import pandas as pd
from .models import Customers, Loans
from datetime import datetime

@shared_task
def import_customer_data(file_path):
    pandas_dataframe = pd.read_excel(file_path)
    for _, row in pandas_dataframe.iterrows():
        Customers.objects.create(
            customer_id = row['Customer ID'],
            first_name = row['First Name'],
            last_name = row['Last Name'],
            phone_number = row['Phone Number'],
            age = row['Age'],
            monthly_salary = row['Monthly Salary'],
            approved_limit = row['Approved Limit'],
            current_debt = row['Current Debt']
        )
    return f"{len(pandas_dataframe)} customers imported successfully."


@shared_task
def import_loan_data(file_path):
    pandas_dataframe = pd.read_excel(file_path)
    for _, row in pandas_dataframe.iterrows():
        try:
            customer = Customers.objects.get(customer_id=row['Customer ID'])
            Loans.objects.create(
                loan_id=row['Loan ID'],
                customer=customer,
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                monthly_installment=row['Monthly payment'],
                EMIs_paid_on_time=row['EMIs paid on Time'],
                Date_Approval_loan=datetime.strptime(row['Date of Approval'], '%d-%m-%Y'),
                end_date=datetime.strptime(row['End Date'], '%d-%m-%Y'),
                status=row['Status']
            )
        except customer.DoesNotExist:
            continue
    return f"{len(pandas_dataframe)} loans imported successfully."