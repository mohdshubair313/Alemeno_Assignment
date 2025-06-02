from celery import shared_task
import pandas as pd
from .models import Customers, Loans
from django.db.utils import IntegrityError


@shared_task
def import_customer_data(file_path):
    pandas_dataframe = pd.read_excel(file_path)
    for _, row in pandas_dataframe.iterrows():
        current_debt = row['Current Debt'] if 'Current Debt' in row else 0
        Customers.objects.create(
            customer_id = row['Customer ID'],
            first_name = row['First Name'],
            last_name = row['Last Name'],
            phone_number = row['Phone Number'],
            age = row['Age'],
            monthly_salary = row['Monthly Salary'],
            approved_limit = row['Approved Limit'],
            current_debt = current_debt
        )
    return f"{len(pandas_dataframe)} customers imported successfully."


@shared_task
def import_loan_data(file_path):
    pandas_dataframe = pd.read_excel(file_path)
    for _, row in pandas_dataframe.iterrows():
        try:
            customer = Customers.objects.get(customer_id=row['Customer ID'])
            
            # Skips if its already exists
            if Loans.objects.filter(loan_id=row['Loan ID']).exists():
                continue

            Loans.objects.create(
                loan_id=row['Loan ID'],
                customer=customer,
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                monthly_installment=row['Monthly payment'],
                EMIs_paid_on_time=row['EMIs paid on Time'],
                Date_Approval_loan=row['Date of Approval'].to_pydatetime(),
                end_date=row['End Date'].to_pydatetime(),
            )
        except Customers.DoesNotExist:
            continue
        except IntegrityError:
            continue  # In case of unexpected conflicts
    return f"{len(pandas_dataframe)} loans imported successfully."
