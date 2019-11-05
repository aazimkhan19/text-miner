from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.mine.models import Text, ModeratedText, Task, Classroom


class TextForm(forms.ModelForm):
    content = forms.CharField(min_length=50, widget=forms.Textarea(), label=_('Эссе'))

    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Тапсыру'), css_class='btn btn-dark'))

    class Meta:
        model = Text
        fields = ('content', )

    def save(self, commit=True):
        # Save the provided password in hashed format
        text = super().save(commit=False)
        return text


class ModerateTextForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial_text = kwargs.pop('initial_text', None)
        super().__init__(*args, **kwargs)
        if initial_text:
            self.fields['content'].initial = initial_text
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Өзгерту'), css_class='btn btn-dark'))

    class Meta:
        model = ModeratedText
        fields = ('content', )
        labels = {
            'content': _('Өзгертілген эссе'),
        }


class CreateTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Құру'), css_class='btn btn-dark'))

    class Meta:
        model = Task
        fields = ('task_level', 'task_title', 'task_description')
        labels = {
            'task_level': _('Тапсырма деңгейі'),
            'task_title': _('Тапсырма атауы'),
            'task_description': _('Тапсырма сипаттамасы'),
        }


class CreateClassroomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateClassroomForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Құру'), css_class='btn btn-dark'))

    class Meta:
        model = Classroom
        fields = ('title', )

        labels = {
                'title': _('Атауы')
        }


class JoinClassroomForm(forms.Form):
    invitation_code = forms.CharField(min_length=8 ,max_length=8, label=_("Сынып коды"))

    def __init__(self, *args, **kwargs):
        super(JoinClassroomForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Қосылу'), css_class='btn btn-dark'))

    def clean_invitation_code(self):
        try:
            classroom = Classroom.objects.get(invitation_code=self.cleaned_data['invitation_code'])
        except Classroom.DoesNotExist:
            raise forms.ValidationError(_("Сынып табылмады"))
        return classroom


class ModifyTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModifyTaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Сақтау'), css_class='btn btn-dark'))

    class Meta:
        model = Task
        fields = ('task_level', 'task_title', 'task_description')
        labels = {
            'task_level': _('Тапсырма деңгейі'),
            'task_title': _('Тапсырма атауы'),
            'task_description': _('Тапсырма сипаттамасы'),
        }