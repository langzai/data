from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .forms import SearchForm


from  .data import * 

dirname = 'IRdata'
index = getIndex(dirname)
v = getFrequencyVector(dirname)
tf = getTf(v)
idf = getIDF(index)
word_weight = getWordWeight(tf,idf)





def search(request):
    if request.method == 'POST' :
        form = SearchForm(request.POST)
        if form.is_valid():
            start_time = time.time()
            search_word = form.cleaned_data['search_word']
            num_return = int(form.cleaned_data['num_return'])
            search_word = search_word.split()
            for i in range(len(search_word)) :
                search_word[i]= search_word[i].strip()
            if (len(search_word) == 1) :
                OptimalFile = getOptimalFileOneWord(search_word[0],word_weight,index,num_return)
                contents = getOneWordContent(OptimalFile,index,search_word[0],dirname)
            else :
                OptimalFile = getOptimalFileTwoWord(search_word,word_weight,index,num_return)
                contents =  getTwoWordContent(OptimalFile , index ,search_word,dirname)
            end_time = time.time()
            form.cleaned_data['search_word'] = search_word
            form.cleaned_data['num_return'] = num_return
            content_list = []
            if contents :
                if (len(search_word) == 1) :
                
                    for title ,weight,content in contents :
                        content_list.append([title,str("%.6f" % weight),content.split()])
                else :
                    for temp_content in contents :
                        for temp1_content in temp_content :
                            title ,weight,content = temp1_content
                            content_list.append([title,str("%.6f"% weight),content.split()])


            return render(request,'contentlist.html',{'form':form,'search_word':search_word,'content_list':content_list,'search_time':end_time - start_time})
        
    else :
        form = SearchForm()
    return render(request,'search.html',{'form':form})


def article(request,title):
    f = open(os.path.join(dirname,title),'r')
    article = f.read()
    return render(request,'detail.html',{'title':title,'article':article})