from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views import View

from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required

from .models import User
from django.db.models import Max, Count, Sum
from django.db.models.functions import TruncMonth
from base.models import Customer, Enquiry, Work, Payment
from .forms import UserForm

from django.core.mail import EmailMultiAlternatives
import threading
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import json
import redis


def is_json_serializable(obj):
    """
    Checks if an object is JSON serializable.
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        # TypeError is raised for non-serializable types.
        # OverflowError is raised for numbers too large for JSON.
        return False



def get_dashboard_data():
    # Getting all the card data
    no_of_customers=Customer.objects.all().count()
    no_of_closed_enq = Enquiry.objects.exclude(status="enquired").count()
    no_of_unclosed_enq = Enquiry.objects.filter(status="enquired").count()
    no_of_cmp_work = Work.objects.filter(status="completed").count()
    no_of_ong_work = Work.objects.filter(status__in=["assigned", "in-progress"]).count()
    no_of_upc_work = Work.objects.filter(status="pending").count()
    card_data={'no_of_customers': no_of_customers, 'no_of_closed_enq': no_of_closed_enq, 'no_of_unclosed_enq': 
        no_of_unclosed_enq, 'no_of_cmp_work': no_of_cmp_work, 'no_of_ong_work': no_of_ong_work, 'no_of_upc_work':
        no_of_upc_work
    }



    # Getting data from monthly enquiry area graph
    end = datetime.now()
    start = (end - relativedelta(months=6)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    months = [] # List having all the past 6 months
    temp = start
    while temp <= end:
        months.append(temp.strftime("%B %y"))
        if temp.month == 12:
            temp = temp.replace(year=temp.year + 1, month=1)
        else:
            temp = temp.replace(month=temp.month + 1)
        
    enquiry_qs = (
        Enquiry.objects
        .filter(created_at__gte=start, created_at__lte=end)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
    ) 

    enquiry_counts = {
        entry['month'].strftime("%B %y"): entry['count']
        for entry in enquiry_qs
    }# Dictionary showing respective months and their enquiry counts

    # Prepare final data list with 0 for months with no data
    no_of_enquiries = [enquiry_counts.get(month, 0) for month in months]
    graph_1 = {'months': months, 'no_of_enquiries': no_of_enquiries}



    # Site Engineer Table
    site_engineers = User.objects.filter(role="engineer")
    site_engineers = [
        {
            "id": obj.id,
            "name": f"{obj.first_name} {obj.last_name}"
        }
        for obj in site_engineers
    ]


    # Doughnut Graph for no of projects
    no_of_pvt_work = Work.objects.filter(project_type__project_type="Private Project").count()
    no_of_gov_work = Work.objects.filter(project_type__project_type="Government Project").count()
    no_of_tot_work = no_of_gov_work+no_of_pvt_work
    graph_2 = {'no_of_tot_work':no_of_tot_work, 'no_of_pvt_work': no_of_pvt_work, 'no_of_gov_work': no_of_gov_work}


    # Payment Due List Table
    payment_due_list = Work.objects.all()
    payment_due_list = [
        {
            "id": obj.id,
            "customer": obj.customer.__str__(),  
            "estimate_amount": float(obj.estimate_amount),      
            "amount_left": float(obj.get_amount_left()),
        }
        for obj in payment_due_list if not obj.is_paid
    ]


    # Payment Mode Graph
    pay_choices = Payment.PAYMENT_CHOICES
    payment_modes = [choice[1] for choice in pay_choices]
    payments = Payment.objects.values('mode').annotate(count=Sum('amount'))
    mode_label_map = dict(pay_choices)
    payments = [
        {'mode': mode_label_map.get(row['mode'], row['mode']), 'count': row['count']}
        for row in payments
    ]
    no_of_payments = {
        payment['mode']: float(payment['count'])
        for payment in payments
    }
    no_of_payments = [no_of_payments.get(mode, 0) for mode in payment_modes]
    graph_3={"payment_modes": payment_modes, 'no_of_payments': no_of_payments}


    context={'card_data': card_data, 'graph_1': graph_1, 'site_engineers': site_engineers, 
            'graph_2': graph_2, 'payment_due_list': payment_due_list, 'graph_3': graph_3}
    
    return context



def get_int_graph(request):
    label_to_code = {label: code for code, label in Payment.PAYMENT_CHOICES}
    mode=request.GET.get("mode")
    mode = label_to_code.get(mode)

    end = datetime.now()
    start = (end - relativedelta(months=6)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    months = [] # List having all the past 6 months
    temp = start
    while temp <= end:
        months.append(temp.strftime("%B %y"))
        if temp.month == 12:
            temp = temp.replace(year=temp.year + 1, month=1)
        else:
            temp = temp.replace(month=temp.month + 1)


    payment_qs = (
        Payment.objects
        .filter(payment_at__gte=start, payment_at__lte=end, mode=mode)
        .annotate(month=TruncMonth('payment_at'))
        .values('month')
        .annotate(count=Sum('amount'))
    ) 

    payment_counts = {
        entry['month'].strftime("%B %y"): entry['count']
        for entry in payment_qs
    }# Dictionary showing respective months and their enquiry counts

    # Prepare final data list with 0 for months with no data
    no_of_payments = [payment_counts.get(month, 0) for month in months]
    graph = {'labels': months, 'data': no_of_payments}
    return JsonResponse(graph)



def event_stream():
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("dashboard_updates")

    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = get_dashboard_data()
                yield f"event: update\ndata: {json.dumps(data)}\n\n"
                time.sleep(0.5)
    except GeneratorExit:
        print("Client disconnected from SSE.")
    finally:
        pubsub.unsubscribe("dashboard_updates")
        pubsub.close()


def sse_dashboard(request):
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response




class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_password_reset_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    subject = "Set your password"
    from_email = 'admin@example.com'
    to_email = [user.email]

    html_content = render_to_string('accounts/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url,
    })
    text_content = f"Hello {user.first_name},\nUse this link to set your password: {reset_url}"

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    EmailThread(email).start()


class DashboardView(RoleRequiredMixin, View):
    template="accounts/dashboard.html"
    required_roles = ['admin', 'assistant', 'engineer', 'manager']

    def get(self, request):
        context=get_dashboard_data()
        return render(request, self.template, context)
    

class UserManagementView(RoleRequiredMixin, View):
    template="accounts/user_management.html"
    model=User
    form_class=UserForm
    required_roles = ['admin', 'manager']

    def get(self, request):
        form_errors = request.session.pop('form_errors', None)
        users=self.model.objects.all().order_by("-is_active")
        context={'form': self.form_class(), 'form_errors': form_errors, 'users': users}
        return render(request, self.template, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_unusable_password()  # User cannot log in until they reset password
            user.save()
            send_password_reset_email(user, request)
            return redirect("users")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("users")
        

class EditUserView(RoleRequiredMixin, View):
    form_class = UserForm
    model=User
    template="accounts/edit_user.html"
    required_roles = ['admin', 'manager']

    def get(self, request, pk):
        user=self.model.objects.get(id=pk)
        form=self.form_class(instance=user)
        context = {'form': form}
        return render(request, self.template, context)
        

    def post(self, request, pk):
        user=self.model.objects.get(id=pk)
        form=self.form_class(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect("users")


@role_required(['admin', 'manager'])
def DropUser(request, pk):
    if request.method=="POST":
        user = User.objects.get(id=pk)
        user.is_active=False
        user.save()
        return HttpResponse("success")