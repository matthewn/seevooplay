from django import forms


class EmailGuestsForm(forms.Form):
    want_reply_yes = forms.BooleanField(
        initial=True,
        label='are coming',
        required=False,
    )
    want_reply_maybe = forms.BooleanField(
        initial=True,
        label='may be coming',
        required=False,
    )
    want_reply_no = forms.BooleanField(
        initial=True,
        label='are not coming',
        required=False,
    )
    want_reply_none = forms.BooleanField(
        initial=True,
        label='have not replied',
        required=False,
    )
    want_have_viewed = forms.BooleanField(
        initial=True,
        label='have viewed the invite',
        required=False,
    )
    want_have_not_viewed = forms.BooleanField(
        initial=True,
        label='have not viewed the invite',
        required=False,
    )
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
