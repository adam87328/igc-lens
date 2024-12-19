from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField()

    # Set a maximum upload file size (e.g., 10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(f"File size exceeds {self.MAX_FILE_SIZE / (1024 * 1024)} MB limit.")
        return file