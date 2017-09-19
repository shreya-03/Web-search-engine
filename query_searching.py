import snowballstemmer
import re,math
import time

stopwords = {}
no_of_doc = 0
stemmer = snowballstemmer.stemmer('english')
tf_idf = {}
dir_dict={0 : "categories", 1 : "references", 2 : "title", 3 : "body", 4 : "external_links", 5 : "infobox"}

class QuerryProcessing:
	def __init__(self,query):
		
		self.query = query
		#self.form = ""

	def preprocessing(self,search_query):
		
		global stopwords
		s = []
		for j in re.compile(r'[^A-Za-z]').split(search_query.lower()):
			if len(j)>0:
				s.append(j.strip())	
		clean_query = []
		for i in range(len(s)):
			if s[i] not in stopwords:
				clean_query.append(stemmer.stemWord(s[i]))
		return clean_query

	def tfidf(self,term,index):
		global no_of_doc,tf_idf
		i=1
		f = open('./Index/'+dir_dict[index]+'/secondary.txt','r')
		file_name = ''
		for i in f:
			if term <= i[i.find(':')+1:-1]:
				file_name = i[:i.find(':')]
				break
		f.close()
		#print file_name
		try:
			f=open(file_name,'r')
		except IOError:
			return
		for i in f:
			if term == i[:i.find(':')]:
				s = i[i.find(':')+1:-1]
				idf = int(s[:s.find(',')])
				s = s[s.find(',')+1:-1]
				l = s.split(',')
				#print l
				l1 = []
				l2 = []
				#print l
				for j in l:
					if ':' in j:
						l1.append(j.split(':')[0])
						l2.append(j.split(':')[1])
		   
				l3 = zip(l1, l2)
				
				l3.sort(reverse=True)
				l3 = l3[:5000]
				#print l3
				N = no_of_doc
				for j in l3:
					#print j[1]
					if j[1] != '':
						if j[0] in tf_idf:
							tf_idf[j[0]]+=int(j[1])*math.log(N/idf)*(6-index)
						else:
							tf_idf[j[0]]=int(j[1])*math.log(N/idf)*(6-index)
				break


	def field_queries(self):
		
		self.query = self.query.strip().split(':')
		field_query = self.query[0]
		i = 1
		while i < len(self.query):
			#print type(term)
			#print term.split(':')	
			#field_query = term.split(':')[0]
			#search_query = term.split(':')[1]
			if i != len(self.query)-1:
				search_query = self.query[i][:-2]
			else:
				search_query = self.query[i]
			#print 'search' + search_query
			clean_query = self.preprocessing(search_query)
			if field_query == 'b':
				field_query = 3
			elif field_query == 'c':
				field_query = 0
			elif field_query == 'e':
				field_query = 4
			elif field_query == 'i':
				field_query = 5
			elif field_query == 'r':
				field_query = 1
			else:
				field_query = 2

			for j in clean_query:
				self.tfidf(j,field_query)
			i += 1
			if i < len(self.query):
				field_query = query[i-1][-1]


	def normal_query(self):
		#global stopwords
		clean_query = self.preprocessing(self.query)
		for i in clean_query:
			for index in range(len(dir_dict)):
				self.tfidf(i,index)

if __name__ == "__main__":
	no_of_query = input()
	f = open('stopwords.txt','r')
	for i in f:
		for j in re.compile(r'[^A-Za-z]').split(i.lower()):
			if len(j)>0:
				stopwords[j.strip()] = True
	f.close()
	f = open('./Index/no_of_doc.txt','r')
	no_of_doc = int(f.readline()[:-1])
	f.close()
	title_id={}
	f = open('./Index/title_id.txt','r')
	for i in f:
		#print i
		i=i.split(':')
		try:
			title_id[i[0]] = i[1].strip()
		except:
			pass
	f.close()
	#print title_id
	while no_of_query > 0 : 
		start_time = time.time()
		tf_idf = {}
		query = input()
		search_object = QuerryProcessing(query)
		if query[1] == ":":
			search_object.field_queries()
		else:
			search_object.normal_query()
		l1 = []
		l2 = []
		for i in tf_idf: 
			l1.append(i)
			l2.append(tf_idf[i])
			
		l3 = zip(l2,l1)

		l3.sort(reverse=True)
	#	print l3[:10]
	#	for (x,y) in l3[:10]:
	#		print x + ' ' + y
	#		print title_id[y]
		i = 0
		while i < 10:
			#print str(l3[i][0]) + ' ' + l3[i][1]
			#print title_id[l3[i][1]]
 			if l3[i][1] in tf_idf.keys():
				print title_id[l3[i][1]]
				i+=1
		print time.time()-start_time
		no_of_query -= 1
	
