from django import forms
from django.db import transaction
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div

from home.models import Gender
from .models import CustomerProfile, CustomerType


class CustomerProfileForm(forms.Form):
    email = forms.EmailField(required=False)
    customer_type = forms.ModelChoiceField(
        queryset=CustomerType.objects.all(), required=False)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    gender = forms.TypedChoiceField(choices=Gender.choices, coerce=int)
    city = forms.CharField(max_length=20, required=False)
    state = forms.CharField(max_length=20, required=False)
    zip_code = forms.IntegerField(required=False)
    contact = PhoneNumberField(required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['email'].initial = user.email
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

        self.customer_profile = CustomerProfile.objects.get(user=self.user)
        self.fields['customer_type'].initial = self.customer_profile.customer_type
        self.fields['gender'].initial = self.customer_profile.gender
        self.fields['city'].initial = self.customer_profile.city
        self.fields['state'].initial = self.customer_profile.state
        self.fields['zip_code'].initial = self.customer_profile.zip_code
        self.fields['contact'].initial = self.customer_profile.contact

        self.fields['first_name'].widget.attrs.update(
            {'autofocus': 'autofocus'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'first_name',
                    'last_name',
                    'gender',
                    'email',
                    'customer_type',
                    css_class='col-md-6',
                ),
                Div(
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

        self.customer_profile.customer_type = data['customer_type']
        self.customer_profile.gender = data['gender']
        self.customer_profile.city = data['city']
        self.customer_profile.state = data['state']
        self.customer_profile.zip_code = data['zip_code']
        self.customer_profile.contact = data['contact']

        if commit:
            with transaction.atomic():
                self.user.save()
                self.customer_profile.save()
        return self.user, self.customer_profile
