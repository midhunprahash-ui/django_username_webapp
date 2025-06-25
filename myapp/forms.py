from django import forms

class UsernameCSVUploadForm(forms.Form):
   
    usernames_csv_file = forms.FileField(label="Upload Usernames CSV")
