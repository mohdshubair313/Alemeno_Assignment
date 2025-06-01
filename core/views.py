from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterCustomerSerializer, CheckEligibilitySerializer, CreateLoanSerializer
from .models import Customers, Loans
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(RegisterCustomerSerializer(customer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------               checking elgibility whether customer is elgible or not

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        customer = Customers.objects.filter(customer_id=data["customer_id"]).first()  # checking customer exists or not
        if not customer:
            return Response({"error": "Customer not found"}, status=404)

        credit_score = 100
        all_loans = customer.loans.all()  # how much loan this customer take 

        # Current loan status
        if customer.current_debt > customer.approved_limit:
            credit_score = 0
        else:
            total_loans = all_loans.count()   # count how many loans this customer has taken
            if total_loans > 0:
                paid_on_time = sum([loan.emis_paid_on_time for loan in all_loans])
                total_emis = sum([loan.tenure for loan in all_loans])
                if total_emis > 0 and paid_on_time / total_emis > 0.8:
                    credit_score += 15

            if total_loans >= 3:
                credit_score += 10

            this_year = date.today().year
            if any(loan.start_date.year == this_year for loan in all_loans):
                credit_score += 10

            total_loan_amt = sum([loan.loan_amount for loan in all_loans])
            if total_loan_amt > 20_00_000:
                credit_score += 15

        # EMI logic
        monthly_installment = (
            data["loan_amount"] * (1 + (data["interest_rate"] / 100)) ** (data["tenure"] / 12)
        ) / data["tenure"]

        if (monthly_installment + customer.current_debt) > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "reason": "EMIs exceed 50% of income"
            }, status=200)

        # Adjust interest_rate if needed
        corrected_rate = data["interest_rate"]
        if credit_score > 50:
            pass
        elif 30 < credit_score <= 50 and corrected_rate <= 12:
            corrected_rate = 13
        elif 10 < credit_score <= 30 and corrected_rate <= 16:
            corrected_rate = 17
        elif credit_score <= 10:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "reason": "Low credit score"
            }, status=200)

        return Response({
            "customer_id": customer.customer_id,
            "approval": True,
            "interest_rate": data["interest_rate"],
            "corrected_interest_rate": corrected_rate,
            "tenure": data["tenure"],
            "monthly_installment": round(monthly_installment, 2),
        }, status=200)

# ---------------         create a loan for the customer
class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        customer = Customers.objects.filter(customer_id=data["customer_id"]).first()
        if not customer:
            return Response({"error": "Customer not found"}, status=404)

        # Calculate monthly_installment
        monthly_installment = (
            data["loan_amount"] * (1 + (data["interest_rate"] / 100)) ** (data["tenure"] / 12)
        ) / data["tenure"]

        start_date = timezone.now().date()
        end_date = start_date + relativedelta(months=data["tenure"])

        loan = Loans.objects.create(
            customer=customer,
            loan_amount=data["loan_amount"],
            interest_rate=data["interest_rate"],
            tenure=data["tenure"],
            monthly_installment=monthly_installment,
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date,
        )

        # Update customer's current debt
        customer.current_debt += monthly_installment
        customer.save()

        return Response({
            "loan_id": loan.id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "monthly_installment": round(monthly_installment, 2),
        }, status=201)
    
# ------------       return the full detailed informations of the customer as well as customer (user)

class ViewLoanDetail(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loans.objects.select_related("customer").get(id=loan_id)
        except Loans.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

        return Response({
            "loan_id": loan.id,
            "customer_id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": round(loan.monthly_installment, 2),
            "tenure": loan.tenure,
            "start_date": loan.start_date,
            "end_date": loan.end_date,
            "emis_paid_on_time": loan.emis_paid_on_time,
        }, status=200)

 # ---------------       return particular customer loans details and all the information

class ViewCustomerLoans(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        loans = customer.loans.all()
        result = []
        for loan in loans:
            result.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "tenure": loan.tenure,
                "monthly_installment": round(loan.monthly_installment, 2),
                "start_date": loan.start_date,
                "end_date": loan.end_date,
                "emis_paid_on_time": loan.emis_paid_on_time,
            })

        return Response({
            "customer_id": customer.customer_id,
            "total_loans": loans.count(),
            "loans": result
        }, status=200)
