from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from ech.users.models import CustomUser
from ech.users.constants.constants import (
    LABEL_PASSWORD,
    LABEL_PASSWORD_CONFIRMATION,
    LABEL_AGE,
    LABEL_COUNTRY,
    LABEL_STATE,
    LABEL_ADDRESS,
    MINIMUM_AGE,
)

from ech.users.constants.messages import (
    MSG_VALIDATION_FAILED_CREDENTIALS,
    MSG_VALIDATION_FAILED_AGE,
)


class BaseUserCreationForm(forms.ModelForm):

    password = forms.CharField(
        label=LABEL_PASSWORD,
        widget=forms.PasswordInput,
        strip=False,
    )

    password_confirmation = forms.CharField(
        label=LABEL_PASSWORD_CONFIRMATION,
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = (
            "user_name",
            "user_email",
            "user_phone",
        )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation:

            if password != password_confirmation:
                raise ValidationError(MSG_VALIDATION_FAILED_CREDENTIALS)

            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        user.email_confirmed = False

        if commit:
            user.save()

        return user


class CommonUserRegistrationForm(BaseUserCreationForm):

    user_age = forms.IntegerField(label=LABEL_AGE)
    user_country = forms.CharField(label=LABEL_COUNTRY)
    user_state = forms.CharField(label=LABEL_STATE)
    user_address = forms.CharField(label=LABEL_ADDRESS)

    class Meta(BaseUserCreationForm.Meta):
        fields = BaseUserCreationForm.Meta.fields + (
            "user_age",
            "user_country",
            "user_state",
            "user_address",
        )

    def clean_user_age(self):
        age = self.cleaned_data.get("user_age")

        if age < MINIMUM_AGE:
            raise ValidationError(MSG_VALIDATION_FAILED_AGE)

        return age

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_role = CustomUser.ROLE_COMMON_USER

        if commit:
            user.save()

        return user


class StaffUserCreationForm(BaseUserCreationForm):

    user_role = forms.ChoiceField(
        choices=[
            (CustomUser.ROLE_SUPPORT_STAFF, "Support Staff"),
            (CustomUser.ROLE_PAYMENT_STAFF, "Payment Staff"),
            (CustomUser.ROLE_PROCCESS_STAFF, "Process Staff"),
            (CustomUser.ROLE_SUPER_STAFF, "Super Staff"),
        ]
    )

    class Meta(BaseUserCreationForm.Meta):
        fields = BaseUserCreationForm.Meta.fields + ("user_role",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_role = self.cleaned_data["user_role"]

        if commit:
            user.save()

        return user
    
class UserProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = (
            "user_name",
            "user_phone",
            "user_country",
            "user_state",
            "user_address",
        )