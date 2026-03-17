from django import forms
from django.utils.translation import gettext_lazy as _


class ResendForm(forms.Form):
    email = forms.EmailField(
        label=_('your email address: '),
        required=True,
    )


class ReplyForm(forms.Form):
    status = forms.ChoiceField(
        label=_('Will you attend?'),
        choices=(
            ('Y', _('Yes')),
            ('N', _('No')),
            ('M', _('Maybe')),
        ),
        widget=forms.RadioSelect,
    )
    extra_guests = forms.IntegerField(
        widget=forms.TextInput,
    )
    comment = forms.CharField(
        label=_('Comments'),
        widget=forms.Textarea,
        required=False,
    )


class EmailGuestsForm(forms.Form):
    want_reply_yes = forms.BooleanField(
        initial=True,
        label=_('are coming'),
        required=False,
    )
    want_reply_maybe = forms.BooleanField(
        initial=True,
        label=_('may be coming'),
        required=False,
    )
    want_reply_no = forms.BooleanField(
        initial=True,
        label=_('are not coming'),
        required=False,
    )
    want_reply_none = forms.BooleanField(
        initial=True,
        label=_('have not replied'),
        required=False,
    )
    want_have_viewed = forms.BooleanField(
        initial=True,
        label=_('have viewed the invite'),
        required=False,
    )
    want_have_not_viewed = forms.BooleanField(
        initial=True,
        label=_('have not viewed the invite'),
        required=False,
    )
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
