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

cache = {}



def search(request):
    if request.method == 'POST' :
        form = SearchForm(request.POST)
        if form.is_valid():
            start_time = time.time()
            search_word = form.cleaned_data['search_word']
            old_search_word = search_word  
            num_return = int(form.cleaned_data['num_return'])
            search_word = wordSegment_1(search_word)
            cache_word = ''
            for word in search_word :
                cache_word = cache_word + word
            '''
            if (len(search_word) == 1) :
                    OptimalFile = getOptimalFileOneWord(search_word[0],word_weight,index,num_return)
                    contents = getOneWordContent(OptimalFile,index,search_word[0],dirname)
            else :
                    OptimalFile = getOptimalFileTwoWord(search_word,word_weight,index,num_return)
                    contents =  getTwoWordContent(OptimalFile , index ,search_word,dirname)
            '''

            
            if cache_word not in cache.keys() :
                if (len(search_word) == 1) :
                    OptimalFile = getOptimalFileOneWord(search_word[0],word_weight,index,num_return)
                    contents = getOneWordContent(OptimalFile,index,search_word[0],dirname)
                else :
                    OptimalFile = getOptimalFileTwoWord(search_word,word_weight,index,num_return)
                    contents =  getTwoWordContent(OptimalFile , index ,search_word,dirname)
                if contents :
                    cache_words ={'num' :num_return ,'searchtime':1,'contents':contents}
                    cache[cache_word] = cache_words 
            
            else :
                if cache[cache_word]['searchtime'] <1000 :
                    cache[cache_word]['searchtime']= cache[cache_word]['searchtime'] + 1
                if num_return < cache[cache_word]['num'] :  
                    contents = cache[cache_word]['contents'][:num_return]
                elif num_return <= cache[cache_word]['num'] :  
                    contents = cache[cache_word]['contents']
                else :
                    if (len(search_word) == 1) :
                        OptimalFile = getOptimalFileOneWord(search_word[0],word_weight,index,num_return)
                        contents = getOneWordContent(OptimalFile,index,search_word[0],dirname)
                    else :
                        OptimalFile = getOptimalFileTwoWord(search_word,word_weight,index,num_return)
                        contents =  getTwoWordContent(OptimalFile , index ,search_word,dirname)
                    cache[cache_word]['num'] = num_return
                    cache[cache_word]['contents'] = contents
            
            if len(cache)>50:
                 temp_word =''  
                 min = 1000
                 for word,word_inf in cache.items():
                        if word_inf['searchtime']  < min :
                            min = word_inf['searchtime']
                            temp_word = word
                 del cache[temp_word]
                   
            
            form.cleaned_data['search_word'] = old_search_word
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

            
            end_time = time.time()
            for word in copy.deepcopy(search_word) :
                search_word.extend([word+'s',word+'es',word +'ed',word + 'ing'])
            search_word.extend(wordSegment(old_search_word))
        
            
            return render(request,'contentlist.html',{'form':form,'search_word':search_word,'content_list':content_list,'search_time':end_time - start_time})
        
    else :
        form = SearchForm()
    return render(request,'search.html',{'form':form})


def article(request,title):
    f = open(os.path.join(dirname,title),'r')
    article = f.read()
    return render(request,'detail.html',{'title':title,'article':article})