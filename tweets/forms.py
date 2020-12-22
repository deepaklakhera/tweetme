from django import forms
from .models import Tweet
from django.conf import settings

MAX_TWEET_LENGTH=settings.MAX_TWEET_LENGTH

class TweetForm(forms.ModelForm):
    
    class Meta:  #Describes the form
        model=Tweet
        fields=['content',]
    
    def clean_content(self):
        
        content=self.cleaned_data.get('content')
        if len(content)>MAX_TWEET_LENGTH:
            raise forms.ValidationError("This tweet is too long")
        return content