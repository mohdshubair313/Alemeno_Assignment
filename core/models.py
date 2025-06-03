from django.db import models
# Create your models here.

class Customers(models.Model):
    customer_id = models.AutoField(primary_key= True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField()
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0.0) # Default to 0.0 


    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_number}"


class Loans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.FloatField()
    tenure = models.IntegerField(help_text="Tenure in months")
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    EMIs_paid_on_time = models.IntegerField()
    Date_Approval_loan = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} - {self.loan_amount} for {self.customer.first_name} {self.customer.last_name}"