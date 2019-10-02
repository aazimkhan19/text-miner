from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from apps.mine.models import Text, ModeratedText, Task, Classroom


class TextForm(forms.ModelForm):
    content = forms.CharField(min_length=50, widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(TextForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', u'Submit'))

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
        self.helper.add_input(Submit('submit', u'Submit'))

    class Meta:
        model = ModeratedText
        fields = ('content', )


class CreateTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', u'Create'))

    class Meta:
        model = Task
        fields = ('task_level', 'task_description')


class CreateClassroomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateClassroomForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-offline-ticket'
        self.helper.form_class = 'OfflineTicket'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', u'Create'))

    class Meta:
        model = Classroom
        fields = ('title', )
