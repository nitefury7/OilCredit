
from django import forms
from django.db import transaction
from phonenumber_field.formfields import PhoneNumberField
from employee.models import EmployeeProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div
from datetime import datetime
from member.models import Invoice, MemberProfile


class OrderForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['member', 'item', 'quantity']

class SetCredit(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['user','credit']

class EmployeeProfileForm(forms.Form):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    gender = forms.ChoiceField(
        choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')))
    city = forms.CharField(max_length=20, required=False)
    state = forms.CharField(max_length=20, required=False)
    zip_code = forms.IntegerField(required=False)
    contact = PhoneNumberField(required=False)
    post = forms.CharField(max_length=20)
    employee_type = forms.ChoiceField(choices = (('T', 'Temporary'), ('P', 'Permanent'),))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['email'].initial = user.email
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

        self.employee_profile = EmployeeProfile.objects.get(user=self.user)
        self.fields['gender'].initial = self.employee_profile.gender
        self.fields['city'].initial = self.employee_profile.city
        self.fields['state'].initial = self.employee_profile.state
        self.fields['zip_code'].initial = self.employee_profile.zip_code
        self.fields['contact'].initial = self.employee_profile.contact
        self.fields['post'].initial = self.employee_profile.post
        self.fields['employee_type'].initial = self.employee_profile.employee_type

        self.fields['first_name'].widget.attrs.update({'autofocus': 'autofocus'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'first_name',
                    'last_name',
                    'gender',
                    'employee_type',
                    'post',
                    css_class='col-md-6',
                ),
                Div(
                    'email',
                    'city',
                    'state',
                    'zip_code',
                    'contact',
                    css_class='col-md-6',
                ),
                css_class='row',
            ),
            ButtonHolder(
                Submit('submit', 'Submit',
                       css_class='btn btn-warning my-2')
            ),
        )

    def save(self, commit=True):
        data = self.cleaned_data
        self.user.email = data['email']
        self.user.first_name = data['first_name']
        self.user.last_name = data['last_name']
        
        self.employee_profile.employment_date = datetime.now()
        self.employee_profile.employee_type = data['employee_type']
        self.employee_profile.post = data['post']
        self.employee_profile.gender = data['gender']
        self.employee_profile.city = data['city']
        self.employee_profile.state = data['state']
        self.employee_profile.zip_code = data['zip_code']
        self.employee_profile.contact = data['contact']

        if commit:
            with transaction.atomic():
                self.user.save()
                self.employee_profile.save()
        return self.user, self.employee_profile
