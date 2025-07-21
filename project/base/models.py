from django.db import models
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Project(models.Model):
    project_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.project_type


class Service(models.Model):
    service_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.service_type
    

class Enquiry(models.Model):
    customer_name = models.CharField(max_length=255)
    mobile_number = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    
    plot_area = models.DecimalField(max_digits=10, decimal_places=2)
    plot_unit = models.CharField(max_length=10, choices=[('acres', 'Acres'), ('cent', 'Cent')], default="acres")
    service_types = models.ManyToManyField(Service)
    project_type = models.ForeignKey(Project, on_delete=models.CASCADE)
    estimate_amount = models.DecimalField(max_digits=12, decimal_places=2)
    proposal_required = models.BooleanField(default=False)

    status=models.CharField(
        max_length=100, 
        choices=[
            ('enquired', 'Enquired'),
            ('business', 'Business'),
            ('dropped', 'Dropped')
        ], 
        default="enquired", 
        blank=True, 
        null=True
    )
    
    heard_from = models.CharField(
        max_length=50,
        choices=[
            ('reference', 'Reference'),
            ('google', 'Google/Website'),
            ('advertisement', 'Advertisement'),
            ('events', 'Events'),
            ('tender', 'Tender')
        ],
        default="google"
    )
    comments = models.TextField(blank=True, null=True)
    next_follow_up = models.DateField(blank=True, null=True)
    
    confirm_as_business = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
    


class Customer(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=128)
    district = models.CharField(max_length=128)

    heard_from = models.CharField(
        max_length=50,
        choices=[
            ('reference', 'Reference'),
            ('google', 'Google/Website'),
            ('advertisement', 'Advertisement'),
            ('events', 'Events'),
            ('tender', 'Tender')
        ],
        default="google"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Work(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    plot_area = models.DecimalField(max_digits=10, decimal_places=2)
    plot_unit = models.CharField(max_length=10, choices=[('acres', 'Acres'), ('cent', 'Cent')], default="acres")
    service_types = models.ManyToManyField(Service)
    project_type = models.ForeignKey(Project, on_delete=models.CASCADE)
    estimate_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    proposal_required = models.BooleanField(default=False)
    status=models.CharField(
        max_length=100, 
        choices=[
            ('pending', 'Pending'),
            ('assigned', 'Assigned'),
            ('in-progress', 'In Progress'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped')
        ], 
        default="pending", 
        blank=True, 
        null=True
    )


    site_visit_on = models.DateTimeField()
    remarks = models.TextField(blank=True, null=True)

    site_engineer=models.ForeignKey(settings.AUTH_USER_MODEL, 
                                    on_delete=models.SET_NULL, null=True, blank=True, 
                                    limit_choices_to={'role': 'engineer'})
    payment_remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_type} - {self.customer.name}"
    

    def get_amount_left(self):
        amount_paid = self.get_amount_paid()
        return self.estimate_amount - amount_paid
    
    def get_amount_paid(self):
        return self.payment_set.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def is_paid(self):
        if self.get_amount_left() == 0:
            return True
        return False    

class Payment(models.Model):
    work = models.ForeignKey(Work, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_at=models.DateTimeField()
    added_at = models.DateTimeField(auto_now_add=True)

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    

