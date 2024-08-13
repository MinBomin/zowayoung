from django import forms
from .models import CounselingSession
from .models import Post 

class CounselingSessionForm(forms.ModelForm):
    class Meta:
        model = CounselingSession
        fields = ['student_name', 'pdf_file']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']