from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from accounts.mixins import RoleRequiredMixin
from accounts.decorators import role_required

from .forms import ServiceForm, ProjectForm, EnquiryForm, FollowUpForm, WorkForm, AssignWorkForm, AddPaymentForm, UpdateWorkStatusForm, AddPaymentRemarkForm
from .models import Service, Project, Enquiry, Work, Payment
from accounts.models import User


@role_required(['admin', 'assistant', 'manager'])
def load_districts(request):
    if request.headers.get('HX-Request') == 'true':
        state = request.GET.get('state', '')
        form = EnquiryForm(state_selected=state)
        html = render_to_string('base/district_form.html', {'form': form})
        return HttpResponse(html)
    




@role_required(['admin', 'manager'])
def DeleteService(request, pk):
    if request.method=="POST":
        service = Service.objects.get(id=pk)
        service.delete()
        return HttpResponse("success")


class ServiceView(RoleRequiredMixin, View):
    template_name="base/service.html"
    form_class = ServiceForm
    model=Service
    required_roles = ['admin', 'manager']

    def get(self, request):
        form=self.form_class()
        services = self.model.objects.all()

        context={'form': form, 'services': services}

        return render(request, self.template_name, context)
    
    
    def post(self, request):
        form=self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("service")
        

class EditServiceView(RoleRequiredMixin, View):
    form_class = ServiceForm
    model=Service
    template="base/edit_service.html"
    required_roles = ['admin', 'manager']

    def get(self, request, pk):
        service=self.model.objects.get(id=pk)
        form=self.form_class(instance=service)
        context = {'form': form}
        return render(request, self.template, context)
        

    def post(self, request, pk):
        service=self.model.objects.get(id=pk)
        form=self.form_class(request.POST, instance=service)

        if form.is_valid():
            form.save()
            return redirect("service")






@role_required(['admin', 'manager'])
def DeleteProject(request, pk):
    if request.method=="POST":
        project = Project.objects.get(id=pk)
        project.delete()
        return HttpResponse("success")


class ProjectView(RoleRequiredMixin, View):
    template_name="base/project.html"
    form_class = ProjectForm
    model=Project
    required_roles = ['admin', 'manager']

    def get(self, request):
        form=self.form_class()
        projects = self.model.objects.all()

        context={'form': form, 'projects': projects}

        return render(request, self.template_name, context)
    
    def post(self, request):
        form=self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("project")
        

class EditProjectView(RoleRequiredMixin, View):
    form_class = ProjectForm
    model=Project
    template="base/edit_project.html"
    required_roles = ['admin', 'manager']

    def get(self, request, pk):
        project=self.model.objects.get(id=pk)
        form=self.form_class(instance=project)
        context = {'form': form}
        return render(request, self.template, context)
        

    def post(self, request, pk):
        project=self.model.objects.get(id=pk)
        form=self.form_class(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("project")
        






class EnquiryView(RoleRequiredMixin, View):
    form_class = EnquiryForm
    model=Enquiry
    template="base/enquiry.html"
    form_template = "base/enquiry_form.html"
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request):
        context={'form': self.form_class()}
        return render(request, self.template, context)
    
    def post(self, request):
        state = request.POST.get('state') 
        form=self.form_class(request.POST, state_selected=state)
        if form.is_valid():
            form.save()
            context={'form': self.form_class(), 'success': True}
            return render(request, self.form_template, context)
        else:
            context={'form': form, 'success': False}
            return render(request, self.form_template, context)
        

class FollowUpView(RoleRequiredMixin, View):
    template="base/follow_up.html"
    model=Enquiry
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request):
        form_errors = request.session.pop('form_errors', None)
        enquiries = Enquiry.objects.filter(status="enquired")
        
        context={'enquiries': enquiries, "form_errors": form_errors}

        return render(request, self.template, context)
    

class EditEnquiryView(RoleRequiredMixin, View):
    form_class = EnquiryForm
    model=Enquiry
    template="base/edit_enquiry.html"
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request, pk):
        enquiry=self.model.objects.get(id=pk)
        form=self.form_class(instance=enquiry, state_selected=enquiry.state)
        context = {'form': form}
        return render(request, self.template, context)
        

    def post(self, request, pk):
        enquiry=self.model.objects.get(id=pk)
        state = request.POST.get('state') 
        form=self.form_class(request.POST, state_selected=state, instance=enquiry)
        if form.is_valid():
            form.save()
            return redirect("follow_up")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("follow_up")
        

class AddFollowUpView(RoleRequiredMixin, View):
    form_class=FollowUpForm
    template="base/follow_up_form.html"
    model=Enquiry
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request, pk):
        enquiry=self.model.objects.get(id=pk)
        form=self.form_class(instance=enquiry)
        context = {'form': form, 'enquiry': enquiry}
        return render(request, self.template, context)
    

    def post(self, request, pk):
        enquiry=self.model.objects.get(id=pk)
        form=self.form_class(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            return redirect("follow_up")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("follow_up")

@role_required(['admin', 'assistant', 'manager'])
def ViewEnquiry(request, pk):
    enquiry = Enquiry.objects.get(id=pk)
    context={'enquiry': enquiry}
    return render(request, "base/view_enquiry.html", context)

@role_required(['admin', 'assistant', 'manager'])
def DropEnquiry(request, pk):
    if request.method=="POST":
        enquiry = Enquiry.objects.get(id=pk)
        enquiry.status = "dropped"
        enquiry.save()
        return HttpResponse("success")
    




class WorkListView(RoleRequiredMixin, View):
    model=Work
    template="base/work_list.html"
    required_roles = ['admin', 'assistant', 'engineer', 'manager']

    def get(self, request):
        form_errors = request.session.pop('form_errors', None)
        if request.user.role == 'engineer':
            works=self.model.objects.exclude(status__in=["completed", "dropped"]).filter(site_engineer=request.user)
        else:
            works=self.model.objects.exclude(status__in=["completed", "dropped"])
        context={'works': works, 'form_errors': form_errors}
        return render(request, self.template, context)
    

@role_required(['admin', 'assistant', 'engineer', 'manager'])
def ViewWork(request, pk):
    work = Work.objects.get(id=pk)
    context={'work': work}
    return render(request, "base/view_work.html", context)


class EditWorkView(RoleRequiredMixin, View):
    form_class = WorkForm
    model=Work
    template="base/edit_work.html"
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request, pk):
        work=self.model.objects.get(id=pk)
        form=self.form_class(instance=work)
        context = {'form': form}
        return render(request, self.template, context)
        

    def post(self, request, pk):
        work=self.model.objects.get(id=pk)
        form=self.form_class(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect("work_list")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("work_list")


@role_required(['admin', 'assistant', 'manager'])
def DropWork(request, pk):
    if request.method=="POST":
        work = Work.objects.get(id=pk)
        work.status = "dropped"
        work.save()
        return HttpResponse("success")
    


class AssignWorkView(RoleRequiredMixin, View):
    template="base/assign_work_form.html"
    model=Work
    form_class=AssignWorkForm
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request, pk):
        work=self.model.objects.get(id=pk)
        context={'work': work, 'form': self.form_class(instance=work)}
        return render(request, self.template, context)
    
    def post(self, request, pk):
        work=self.model.objects.get(id=pk)
        form = self.form_class(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect("work_list")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("work_list")








class DroppedListView(RoleRequiredMixin, View):
    model=Enquiry
    template="base/dropped_list.html"
    required_roles = ['admin', 'assistant', 'manager']

    def get(self, request):
        enquiries=self.model.objects.filter(status="dropped")
        context={'enquiries': enquiries}
        return render(request, self.template, context)
    

@role_required(['admin', 'assistant', 'manager'])
def ViewDropped(request, pk):
    enquiry = Enquiry.objects.get(id=pk)
    context={'enquiry': enquiry}
    return render(request, "base/view_dropped.html", context)





class CompletedWorkListView(RoleRequiredMixin, View):
    model=Work
    template="base/completed_work_list.html"
    required_roles = ['admin', 'assistant', 'engineer', 'manager']

    def get(self, request):
        if request.user.role == 'engineer':
            works=self.model.objects.filter(site_engineer=request.user, status="completed")
        else:
            works=self.model.objects.filter(status="completed")
        context={'works': works}
        return render(request, self.template, context)
    

@role_required(['admin', 'assistant', 'engineer', 'manager'])
def ViewCompletedWork(request, pk):
    work = Work.objects.get(id=pk)
    context={'work': work}
    return render(request, "base/view_completed_work.html", context)


class WorkPaymentView(RoleRequiredMixin, View):
    model=Work
    template="base/work_payment.html"
    required_roles = ['admin', 'assistant', 'engineer', 'manager']

    def get(self, request, pk):
        work=self.model.objects.get(id=pk)
        payments = Payment.objects.filter(work=work)
        context={'work': work, 'payments': payments}
        return render(request, self.template, context)
    


class AddPaymentView(RoleRequiredMixin, View):
    template="base/add_payment.html"
    required_roles = ['assistant']
    form_class = AddPaymentForm

    def get(self, request, pk):
        work = Work.objects.get(id=pk)
        context={'work': work, 'form': self.form_class()}
        return render(request, self.template, context)
    
    def post(self, request, pk):
        work = Work.objects.get(id=pk)
        form=self.form_class(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.work=work
            payment.save()
            return redirect("work_list")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("work_list")
        

class UpdateWorkStatusView(RoleRequiredMixin, View):
    model=Work
    template="base/update_work_status.html"
    form_class=UpdateWorkStatusForm
    required_roles = ['engineer']

    def get(self, request, pk):
        work = Work.objects.get(id=pk)
        context={'work': work, 'form': self.form_class(instance=work)}
        return render(request, self.template, context)
    
    def post(self, request, pk):
        work = Work.objects.get(id=pk)
        form=self.form_class(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect("work_list")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("work_list")
        

class AddPaymentRemarkView(RoleRequiredMixin, View):
    model=Work
    template="base/add_payment_remark.html"
    form_class=AddPaymentRemarkForm
    required_roles = ['engineer']

    def get(self, request, pk):
        work = Work.objects.get(id=pk)
        context={'work': work, 'form': self.form_class(instance=work)}
        return render(request, self.template, context)
    
    def post(self, request, pk):
        work = Work.objects.get(id=pk)
        form=self.form_class(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect("work_list")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    label=field.replace('_', ' ').capitalize()
                    errors.append(f"{label}: {error}")

            request.session['form_errors'] = errors
            return redirect("work_list")
        



class PaymentsView(RoleRequiredMixin, View):
    template="base/payments.html"
    model=Payment
    required_roles=['admin', 'manager']

    def get(self, request):
        payments = self.model.objects.all()
        context={'payments': payments}
        return render(request, self.template, context)
    


class PaymentDueListView(RoleRequiredMixin, View):
    template="base/payment_due_list.html"
    required_roles=['admin', 'manager', 'assistant']

    def get(self, request):
        payment_due_list = Work.objects.all()
        payment_due_list = [obj for obj in payment_due_list if not obj.is_paid]
        context={'payment_due_list': payment_due_list}
        return render(request, self.template, context)



class SiteEngStatusListView(RoleRequiredMixin, View):
    template="base/site_eng_status_view.html"
    required_roles=['admin', 'manager', 'assistant']

    def get(self, request):
        site_engineers = User.objects.filter(role="engineer")
        context={'site_engineers': site_engineers}
        return render(request, self.template, context)
    

class SiteEngStatusView(RoleRequiredMixin, View):
    template="base/site_eng_status.html"
    required_roles=['admin', 'manager', 'assistant']

    def get(self, request, pk):
        Eng = User.objects.get(id=pk)
        works = Work.objects.filter(site_engineer=Eng)
        context={'works': works, 'eng': Eng}
        return render(request, self.template, context)