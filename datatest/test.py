from  data import * 

dirname = 'IRdata1'
index = getIndex(dirname)
v = getFrequencyVector(dirname)
tf = getTf(v)
idf = getIDF(index)
word_weight = getWordWeight(tf,idf)


start_time = time.time()
OptimalFile = getOptimalFileTwoWord(['sho','36'],word_weight,index,10)
contents =  getTwoWordContent(OptimalFile , index ,['sho','36'],dirname)
print(contents)
end_time = time.time()
print(end_time - start_time)
print()


start_time = time.time()
OptimalFile = getOptimalFileOneWord('12',word_weight,index,10)
contents = getOneWordContent(OptimalFile,index,'12',dirname)
#print(OptimalFile)
print(contents)
end_time = time.time()
print(end_time - start_time)
print()

