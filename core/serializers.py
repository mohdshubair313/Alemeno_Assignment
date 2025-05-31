from rest_framework import serializers
from .models import Customers, Loans
from helper import calculate_approved_limit

class RegisterCustomerSerializer(serializers.ModelSerializer):
    monthly_income = serializers.FloatField(write_only=True)

    class Meta:
        model = Customers
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 'approved_limit']
        read_only_fields = ['customer_id', 'approved_limit']

    def create(self, validated_data):
        income = validated_data.pop("monthly_income")
        approved_limit = calculate_approved_limit(income)
        customer = Customers.objects.create(
            **validated_data,
            monthly_salary=income,
            approved_limit=approved_limit,
        )
        return customer

# checking eligibility whether customer is eligible or not
class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

# creating a new loan for the customer
class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()