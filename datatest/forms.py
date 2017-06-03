from django import forms

class SearchForm(forms.Form):
    search_word = forms.CharField(initial='data',label='',widget=forms.TextInput({'class':"search_txt"}))
    num_return = forms.CharField(initial='10',label='',widget=forms.TextInput({'class':"search_num"}))

