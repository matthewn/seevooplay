from django import forms


class EmailGuestsForm(forms.Form):
    want_reply_yes = forms.BooleanField(
        label='are coming',
        required=False,
    )
    want_reply_no = forms.BooleanField(
        label='are not coming',
        required=False,
    )
    want_reply_maybe = forms.BooleanField(
        label='may be coming',
        required=False,
    )
    want_reply_none = forms.BooleanField(
        label='have not replied',
        required=False,
    )
    want_have_viewed = forms.BooleanField(
        label='have viewed the invite',
        required=False,
    )
    want_have_not_viewed = forms.BooleanField(
        label='have not viewed the invite',
        required=False,
    )
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
