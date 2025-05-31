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
    current_debt = models.FloatField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_number}"
    # class Meta:
    #     db_table = 'customers'
    #     verbose_name = 'Customer'
    #     verbose_name_plural = 'Customers'
    #     ordering = ['last_name', 'first_name']


class Loans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField(help_text="Tenure in months")
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    EMIs_paid_on_time_or_not = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Loan {self.loan_id} - {self.loan_amount} for {self.customer.first_name} {self.customer.last_name}"
    # class Meta:
    #     db_table = 'loans'
    #     verbose_name = 'Loan'
    #     verbose_name_plural = 'Loans'
    #     ordering = ['start_date']