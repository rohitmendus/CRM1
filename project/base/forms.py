from django import forms

from phonenumber_field.formfields import SplitPhoneNumberField
from phonenumbers.phonenumberutil import region_code_for_country_code
from tempus_dominus.widgets import DatePicker, DateTimePicker
from django_select2.forms import Select2MultipleWidget

from .models import Service, Project, Enquiry, Work, Customer, Payment
from django.core.cache import cache
from django.conf import settings

import requests
import datetime


today = str(datetime.datetime.today())

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields=['service_type']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields=['project_type']


class EnquiryForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[])
    district = forms.ChoiceField(choices=[])
    mobile_number = SplitPhoneNumberField()
    next_follow_up=forms.DateField(
        input_formats = settings.DATE_INPUT_FORMATS,
        label='Next Follow-up',
        required=False
    )

    site_visit_on = forms.DateTimeField(
        input_formats = settings.DATETIME_INPUT_FORMATS,
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=False
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        label="Remarks"
    )


    class Meta:
        model=Enquiry
        fields="__all__"
        widgets = {
            'plot_unit': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'heard_from': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'service_types': Select2MultipleWidget,
        }



    def __init__(self, *args, **kwargs):
        state_selected = kwargs.pop('state_selected', None)

        super().__init__(*args, **kwargs)

        # Set minDate to today if it's a new form (i.e., not editing an existing instance)
        # Set minDate to instance's date if it's an edit form
        if not self.instance.pk:
            self.fields['next_follow_up'].widget = DatePicker(
                attrs={
                    'append': 'fa fa-calendar',
                    'class': 'form-control',
                },
                options={
                    'minDate': today
                }
            )
        else:
            self.fields['next_follow_up'].widget = DatePicker(
                attrs={
                    'append': 'fa fa-calendar',
                    'class': 'form-control',
                },
                options={
                    'minDate': str(self.instance.next_follow_up)
                }
            )



        # To load instance's mobile number region in the dropdown for edit form
        if self.initial.get('mobile_number'):
            phone = self.initial['mobile_number']
            if phone and hasattr(phone, 'country_code'):
                numeric_code = phone.country_code  
                region_code = region_code_for_country_code(numeric_code)  
                self.initial['mobile_number_country'] = region_code

            
        # Fetching states and corresponding districts from API
        # Step 1: Try fetching from cache
        states = cache.get('api_state')

        if not states:
            try:
                # Step 2: Fetch from external API
                api_url = "https://api.data.gov.in/resource/a71e60f0-a21d-43de-a6c5-fa5d21600cdb?api-key=579b464db66ec23bdd000001f773f16fe314448f6aa7cf50db461801&format=json&limit=100"
                response = requests.get(api_url)

                if response.status_code == 200:
                    data=response.json()
                    data = data["records"]
                    states = [(item['state_name_english'], item['state_name_english']) for item in data]
                    states.sort()

                # Step 3: Cache it for 1 hour
                cache.set('api_state', states, timeout=3600)

            except Exception as e:
                # Step 4: Fail safe
                states = []

        # Step 5: Set form field choices
        self.fields['state'].choices = [('', '-- Select a state --')] + states

        # Dynamic district choices if state is selected
        if state_selected:
            districts = cache.get(f"districts_{state_selected}")
            if not districts:
                try:
                    api_url = f"https://api.data.gov.in/resource/37231365-78ba-44d5-ac22-3deec40b9197?api-key=579b464db66ec23bdd000001f773f16fe314448f6aa7cf50db461801&format=json&limit=100&filters%5Bstate_name_english%5D={state_selected}"
                    response = requests.get(api_url)

                    if response.status_code == 200:
                        data=response.json()
                        data = data["records"]
                        districts = [(item['district_name_english'], item['district_name_english']) for item in data]
                        cache.set(f"districts_{state_selected}", districts, timeout=3600)
                except:
                    districts = []
            self.fields['district'].choices = [('', '-- Select a district --')] + districts
        else:
            self.fields['district'].choices = [('', '-- Select a state first --')]


    
    def save(self, commit=True):
        enquiry = super().save(commit=commit)

        # Only if confirmed as business, insert into Customer & Work
        if enquiry.confirm_as_business:
            # 1. Create Customer
            customer, created = Customer.objects.get_or_create(
                mobile_number=enquiry.mobile_number,
                name=enquiry.customer_name,
                defaults={
                    'email': enquiry.email,
                    'address': enquiry.address,
                    'landmark': enquiry.landmark,
                    'state': enquiry.state,
                    'district': enquiry.district,
                    'heard_from': enquiry.heard_from,
                }
            )

            # 2. Create Work (multiple services handled)
            site_visit_on = self.cleaned_data.get('site_visit_on')
            remarks = self.cleaned_data.get('remarks')

            work = Work.objects.create(
                    customer=customer,
                    plot_area=enquiry.plot_area,
                    plot_unit=enquiry.plot_unit,
                    project_type=enquiry.project_type,
                    estimate_amount=enquiry.estimate_amount,
                    proposal_required=enquiry.proposal_required,
                    site_visit_on=site_visit_on,
                    remarks=remarks,
                )
            
            work.service_types.set(enquiry.service_types.all())

            enquiry.status = 'business'
            if commit:
                enquiry.save()

        return enquiry


class FollowUpForm(forms.ModelForm):
    next_follow_up=forms.DateField(
        input_formats = settings.DATE_INPUT_FORMATS,
        label='Next Follow-up',
        required=False
    )

    site_visit_on = forms.DateTimeField(
        input_formats = settings.DATETIME_INPUT_FORMATS,
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=False
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        label="Remarks"
    )

    class Meta:
        model=Enquiry
        fields=["comments", "next_follow_up", "status"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['next_follow_up'].widget = DatePicker(
                attrs={
                    'append': 'fa fa-calendar',
                    'class': 'form-control',
                },
                options={
                    'minDate': str(self.instance.next_follow_up)
                }
            )
    

    def save(self, commit=True):
        enquiry = super().save(commit=commit)

        # Only if confirmed as business, insert into Customer & Work
        if enquiry.status=="business":
            # 1. Create Customer
            customer, created = Customer.objects.get_or_create(
                mobile_number=enquiry.mobile_number,
                name=enquiry.customer_name,
                defaults={
                    'email': enquiry.email,
                    'address': enquiry.address,
                    'landmark': enquiry.landmark,
                    'state': enquiry.state,
                    'district': enquiry.district,
                    'heard_from': enquiry.heard_from,
                }
            )

            # 2. Create Work (multiple services handled)
            site_visit_on = self.cleaned_data.get('site_visit_on')
            remarks = self.cleaned_data.get('remarks')

            work = Work.objects.create(
                    customer=customer,
                    plot_area=enquiry.plot_area,
                    plot_unit=enquiry.plot_unit,
                    project_type=enquiry.project_type,
                    estimate_amount=enquiry.estimate_amount,
                    proposal_required=enquiry.proposal_required,
                    site_visit_on=site_visit_on,
                    remarks=remarks,
                )
            
            work.service_types.set(enquiry.service_types.all())

            enquiry.confirm_as_business = True
            if commit:
                enquiry.save()

        return enquiry
    


class WorkForm(forms.ModelForm):
    site_visit_on = forms.DateTimeField(
        input_formats = settings.DATETIME_INPUT_FORMATS,
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=True
    )

    class Meta:
        model=Work
        exclude=("customer",)
        widgets = {
            'plot_unit': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'service_types': Select2MultipleWidget,
        }


class AssignWorkForm(forms.ModelForm):
    class Meta:
        model=Work
        fields=["site_engineer"]

    def save(self, commit=True):
        work = super().save(commit=False)
        if self.cleaned_data.get('site_engineer') is None:
            work.status = "pending"
        else:
            work.status = "assigned"
        work.save()

        return work
    

class AddPaymentForm(forms.ModelForm):
    payment_at = forms.DateTimeField(
        input_formats = settings.DATETIME_INPUT_FORMATS,
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
        required=True
    )

    class Meta:
        model=Payment
        fields=['amount', 'payment_at', 'mode']


class UpdateWorkStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[
        ('assigned', 'Assigned'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed')
    ])

    class Meta:
        model=Work
        fields=['status']


class AddPaymentRemarkForm(forms.ModelForm):
    class Meta:
        model=Work
        fields=['payment_remarks']