import xml.sax,os,re
import sys
import time
from collections import defaultdict
#import Stemmer
import snowballstemmer
from heapq import *
import glob

stemmer = snowballstemmer.stemmer('english')
#stemmer = Stemmer.Stemmer('english')
stopwords ={}
dicts = {'categories' : {}, 'references' : {},'title' : {}, 'body' : {},'external_links' : {},'infobox' :{}}
dir_list=["categories","references","title","body","external_links","infobox"]
file_count = 1
no_of_doc = 0
count = 0
documents_per_file = 20000
lines_per_doc = 8000

ft = open('./Index/title_id.txt','w')

class contenthandler(xml.sax.ContentHandler):
	
	def __init__(self):
		xml.sax.ContentHandler.__init__(self)
		self.doc_id = ""
		self.text = ""
		self.title = ""
		self.content = ""
		self.body = ""
		self.external_links = ""
		self.references = ""
		self.categories = ""
		self.infobox = ""
		self.current = ""
		self.parent = ""
		self.elements = []

	def startElement(self,name,attrs):
		
		self.elements.append(name)
		if self.current:
			self.parent = self.current
		self.current = name
		
	def endElement(self,name):
		
		if name == 'page':
			global no_of_doc,count,file_count,dicts
			no_of_doc += 1 
			count += 1
			self.preprocessing(self.categories.lower(),'categories')
			self.preprocessing(self.references.lower(),'references')
			self.preprocessing(self.title.lower(),'title')
			self.preprocessing(self.body.lower(),'body')
			self.preprocessing(self.external_links.lower(),'external_links')
			self.preprocessing(self.infobox.lower(),'infobox')
			if count == documents_per_file:
				for key in dir_list:
					write_to_file(key, opfilepath + '/' + key)
					#print 'key :' + key + 'file count :' + str(file_count)
				dicts.clear()
				dicts = {'categories' : {}, 'references' : {},'title' : {}, 'body' : {},'external_links' : {},'infobox' :{}}
				file_count += 1
				count = 0
			ft.write(str(self.doc_id.rstrip('\n'))+':'+str(self.title))

		if name == 'id':
			#global no_of_doc
			if self.parent == 'page':
				self.doc_id = self.content
			#	no_of_doc += 1
				#print 'document with id: ' + self.doc_id
		
		if name == 'title':
			self.title = self.content
			#ft.write(str(self.doc_id)+':'+str(self.title))
			#if self.doc_id != "":
			#	ft.write(self.title + ":" + str(self.doc_id))
		
		if name == 'text':
			self.text = self.content
			self.parse_text()
#			self.categories,self.external_links,self.references,self.body,self.infobox = parse_text(self.text)

		# to get only one id so poping elements
		self.elements.pop()
		if self.elements:
			self.current = self.parent
			if len(self.elements) ==1:
				self.parent=""
			else:
				self.parent= self.elements[-1]
		else:
			self.current=""
		self.content =""
		

	def characters(self,content):

		uni = content.encode('utf-8').strip()
		if uni:
			self.content = self.content + uni + '\n'
	
	def preprocessing(self,text,flag):
		
		text = re.sub(r'[^A-Za-z]', ' ', text)
		clean_text = text.split(' ')
		content = {}
		global dicts
		global stopwords
		for i in range(len(clean_text)):
			if stemmer.stemWord(clean_text[i]) not in stopwords and len(clean_text[i])>0:
				if stemmer.stemWord(clean_text[i]) not in content:
					content[stemmer.stemWord(clean_text[i])]=1
				else:
					content[stemmer.stemWord(clean_text[i])]+=1
		for (key,value) in content.iteritems():
			if key not in dicts[flag]:
				dicts[flag][key]=[1, str(self.doc_id.strip())+":"+str(value)+","]
			else:
				dicts[flag][key][0]+=1
				dicts[flag][key][1]+=str(self.doc_id.strip())+":" + str(value)+","			
		#content.clear()

	def  parse_text(self):

		sentences =  self.text.strip()
		sentences = sentences.split('\n')
		self.categories = ""
		self.external_links = ""
		self.references = ""
		self.body = ""
		self.infobox = ""
		flag = 0
		for line in sentences:
		
			if line.startswith("{{Infobox"):
				flag = 1
				continue
			elif flag == 1 and line == "}}":
				flag = 0
				continue
			elif line.startswith("==References=="):
				flag = 2
				continue
			elif flag ==2 and (( line.startswith("==")  and line.find("Reference")==-1) or line.startswith("[[Category:") or line.startswith("{{")):
				flag=0
			elif flag ==3 and ( line.startswith("[[Category:")):
				flag = 0
				continue
			elif line.startswith("==External links=="):
				flag = 3
				continue
	
			if line.startswith("[[Category:"):
				#print "entered category case" + '\n'
				self.categories += line[11:-2] + '\n'
			elif flag==0:
				#print "entered body case" + '\n'
				self.body += line + '\n'
			elif flag ==1:
				#print "entered infobox case" + '\n' 
				self.infobox+=line+'\n'
			elif flag ==2:
				#print "entered references case" + '\n'
				self.references += line + '\n'
			elif flag ==3:
				#print "entered links case" + '\n'
				self.external_links +=line +'\n'

class ExternalMerge:

	def __init__(self,directory):
		
		self.file_name = directory + '/final'
		self.sec_file_name = directory + '/secondary.txt'
		self.directory = directory
		self.sub_count = 1
		self.latest_word = ""
		self.line_count = 0
		self.file_pointer = []
		self.l = []
		self.count = 0

	def write_to_heap(self):
		
		global file_count
		for i in xrange(1,file_count+1):
			f0 = open(self.directory+'/file'+str(i)+'.txt','r') 
			s = f0.readline()[:-1]
			s1 = s[:s[:s.find(',')].find(':')]
			self.l.append((s1, s, f0))
			self.file_pointer.append(f0)
		heapify(self.l)

	def merge(self):
		
		global lines_per_doc
		f_sec = open(self.sec_file_name,'w')
		f = open(self.file_name + str(self.sub_count) + ".txt",'w')
		while(self.count < file_count):
			top = heappop(self.l)
			s0 = top[0]
			s1 = top[1]
			f1 = top[2]
			s_list = []
			s_list.append(s1)
			s = f1.readline()[:-1]
			if s == '':
				self.count+=1
			else:
				heappush(self.l, (s[:s[:s.find(',')].find(':')], s, f1))

			if self.count == file_count:
				break

			while(1):
				try:
					tmp = heappop(self.l)
				except IndexError:
					break
				s0 = tmp[0]
				s2 = tmp[1]
				f2 = tmp[2]
				#print s2
				#print s_list[-1][:s_list[-1][:s2[-1].find(',')].find(':')]
				if s0 != s_list[-1][:s_list[-1][:s2[-1].find(',')].find(':')]:
					heappush(self.l,(s0,s2,f2))
					break
				else:
					s_list.append(s2)
					s3 = f2.readline()[:-1]
					#print s3
					if s3 == '':
						self.count += 1
					else:
						heappush(self.l,(s3[:s3[:s3.find(',')].find(':')],s3,f2))

			if len(s_list) == 1:
				s = s_list[0]
				self.line_count+=1
				self.latest_word = s[:s.find(':')]
				#print self.latest_word
				f.write(s+'\n')
				if self.line_count == lines_per_doc: 
				   self.line_count = 0
				   f.close()
				   f_sec.write(self.file_name + str(self.sub_count)+".txt"+":"+self.latest_word+'\n')
				   self.sub_count += 1
				   f = open(self.file_name+str(self.sub_count)+".txt",'w')
				
			else:
				word_pre = s_list[0][:s_list[0].find(',')]
				word = word_pre[:word_pre.find(':')]
				tgif = 0
				s = ""
				flag = 0
				for i in s_list:
					content = i[i.find(',')+1:]
					content_pre = i[:i.find(',')]
					tgif_tmp = int(content_pre[content_pre.find(':')+1:])
					tgif += tgif_tmp
					if flag == 0:
						s = content
						flag = 1
					else:
						s += ','+ content
			#print word+':'+str(tgif)+','+s+'\n'
				self.line_count += 1
				self.latest_word = word
				f.write(word+':'+str(tgif)+','+s+'\n')
				if self.line_count == lines_per_doc:
				   self.line_count=0
				   f.close()
				   f_sec.write(self.file_name + str(self.sub_count)+".txt"+":"+word+'\n')
				   self.sub_count += 1
				   f = open(self.file_name+str(self.sub_count)+".txt",'w')
		if f:
			f.close()

		if self.line_count>0:
			f_sec.write(self.file_name + str(self.sub_count)+".txt"+":"+self.latest_word+'\n')
			
		f_sec.close()

		for i in self.file_pointer:	
			i.close()

def write_to_file(flag,directory):
	
	#global dicts,file_count
	global dicts
	global file_count
	if not os.path.exists(directory):
		os.makedirs(directory)
	keys = dicts[flag].keys()
	keys.sort()
	f = open(directory+'/file'+str(file_count)+".txt",'w')
	for i in keys:
		freq = dicts[flag][i][0]
		doc_list = dicts[flag][i][1][:-1]	
		final = i+":"+str(freq)+","+doc_list+'\n'
		f.write(final)
	f.close()


if __name__ == "__main__":
	#start_time = time.time()
	ipfilepath = sys.argv[1]
	opfilepath = sys.argv[2]
	f = open('stopwords.txt','r')
	for i in f:
		for j in re.compile(r'[^A-Za-z]').split(i.lower()):
			if len(j)>0:
				stopwords[j.strip()] = True
	f.close()
	source = open(ipfilepath,'r')
	xml.sax.parse(source,contenthandler())
	ft.close()
	#print "before writing to file"
	for key in dir_list:
		write_to_file(key,opfilepath+'/'+key)
		#os.remove(glob.glob(opfilepath + '/' + key + '/file*'))
		merge_object = ExternalMerge(opfilepath + '/' + key)
		merge_object.write_to_heap()
		merge_object.merge()
		for filename in glob.glob(opfilepath + '/' + key + '/file*'):
			os.remove(filename)

	
	f = open(opfilepath + "/no_of_doc.txt",'w'	)
	f.write(str(no_of_doc) + '\n')
	f.close()	
	
	#print time.time()-start_time