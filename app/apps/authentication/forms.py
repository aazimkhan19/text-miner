from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django.contrib.auth.models import Group

from apps.authentication.models import User

from apps.mine.models import Miner

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    role = forms.TypedChoiceField(choices=((1, 'miner'), (2, 'moderator'),), empty_value=1, coerce=int)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.helper.layout = Layout(
            Field('email', css_class="form-control form-input"),
            Field('phone', css_class="form-control form-input"),
            Field('first_name', css_class="form-control form-input"),
            Field('last_name', css_class="form-control form-input"),
            Field('role', css_class="form-control form-input"),
            Field('password1', css_class="form-control form-input"),
            Field('password2', css_class="form-control form-input"),
            Submit('submit', 'Sign Up', css_class="btn btn-lg btn-dark btn-block")
        )

    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError('email field is not provided')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with this Email is already in use')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            raise forms.ValidationError('phone field is not provided')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('User with this Phone is already in use')
        return phone

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if not role:
            raise forms.ValidationError('Role is not provided')
        if role not in [1, 2]:
            raise forms.ValidationError('Role can be either miner or moderator')
        return role

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        role = self.cleaned_data["role"]
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if role == 1:
                group = Group.objects.get(name='miner')
                group.user_set.add(user)
                Miner.objects.create(user=user)
            else:
                group = Group.objects.get(name='moderator')
                group.user_set.add(user)
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('email', 'password',
                  'first_name', 'last_name',
                  'date_joined', 'is_superuser',
                  'is_admin', 'phone')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 and not password2:
            return None
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if self.cleaned_data['password2']:
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
        return user


class UserAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserAuthForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        #form-control form-input
        self.helper.layout = Layout(
            Field('username', css_class="form-control form-input"),
            Field('password', css_class="form-control form-input"),
            Submit('submit', 'Sign In', css_class="btn btn-lg btn-dark btn-block")
        )


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

    class Meta:
        model = User
        fields = ('email', 'first_name',
                  'last_name', 'phone')
