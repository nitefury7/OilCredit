from datetime import datetime

from django import forms
from django.db import transaction
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div

from home.models import Gender
from member.models import MemberProfile, MemberType, Invoice


class OrderForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['item', 'quantity']

    def __init__(self, member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = member
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('item', css_class='col-md-6'),
                Div('quantity', css_class='col-md-6'),
                css_class='row',
            ),
            ButtonHolder(Submit('submit', 'Submit',
                         css_class='btn btn-warning my-2')),
        )

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data['item'].rate * cleaned_data['quantity']
        if (self.member.credit < cost):
            self.add_error( 'quantity', f'You do not have sufficient credits.')
        self.member.credit -= cost

    def save(self, commit=True):
        invoice = super().save(commit=False)
        invoice.member = self.member
        invoice.order_timestamp = datetime.now()
        if commit:
            invoice.member.save()
            invoice.save()
        return (invoice, invoice.member)


class AddCredit(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['credit']


class MemberProfileForm(forms.Form):
    email = forms.EmailField(required=False)
    member_type = forms.ModelChoiceField(
        queryset=MemberType.objects.all(), required=False)
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

        self.member_profile = MemberProfile.objects.get(user=self.user)
        self.fields['member_type'].initial = self.member_profile.member_type
        self.fields['gender'].initial = self.member_profile.gender
        self.fields['city'].initial = self.member_profile.city
        self.fields['state'].initial = self.member_profile.state
        self.fields['zip_code'].initial = self.member_profile.zip_code
        self.fields['contact'].initial = self.member_profile.contact

        self.fields['first_name'].widget.attrs.update({'autofocus': 'autofocus'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'first_name',
                    'last_name',
                    'gender',
                    'email',
                    'member_type',
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

        self.member_profile.member_type = data['member_type']
        self.member_profile.gender = data['gender']
        self.member_profile.city = data['city']
        self.member_profile.state = data['state']
        self.member_profile.zip_code = data['zip_code']
        self.member_profile.contact = data['contact']

        if commit:
            with transaction.atomic():
                self.user.save()
                self.member_profile.save()
        return self.user, self.member_profile
