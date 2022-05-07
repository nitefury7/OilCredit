from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from member.models import MemberProfile, MemberType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div
from django.contrib.auth.password_validation import (
    CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator, password_validators_help_text_html,)


validators = [CommonPasswordValidator(), MinimumLengthValidator(8),
              NumericPasswordValidator()]


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput(
    ), validators=(x.validate for x in validators), help_text=password_validators_help_text_html(validators))
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=False)
    member_type = forms.ModelChoiceField(queryset=MemberType.objects.all())
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    gender = forms.ChoiceField(
        choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')))
    city = forms.CharField(max_length=20, required=False)
    state = forms.CharField(max_length=20, required=False)
    zip_code = forms.IntegerField(required=False)
    contact = PhoneNumberField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': 'autofocus'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'username',
                    'password',
                    'confirm_password',
                    'email',
                    'member_type',
                    css_class='col-md-6',
                ),
                Div(
                    'first_name',
                    'last_name',
                    'gender',
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
                       css_class='btn btn-warning button white my-2')
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            self.add_error('username', 'Username already taken')

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', "Passwords don't match")

    def save(self, commit=True):
        data = self.cleaned_data
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        user.set_password(data['password'])
        member_profile = MemberProfile(
            user=user,
            member_type=data['member_type'],
            gender=data['gender'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            contact=data['contact'],
        )
        if commit:
            with transaction.atomic():
                user.save()
                member_profile.save()
        return user, member_profile
