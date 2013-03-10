#!/usr/bin/python
import cherrypy
from pymongo import *
import os
import time

#boot up mongo
os.system('(mongod --dbpath datadir > datadir/log.txt) &')
time.sleep(1)
webpageDirectory="pages/"
c=Connection()



def header():
	output=''
	f=open('pages/header.html','r')
	for l in f: output+=l
	return output

def footer():
	output=''
        f=open('pages/footer.html','r')
        for l in f: output+=l
        return output

class Index(object):
	def verifyUser(self):
		verified=0
		try: 
			cherrypy.session['login']
			verified=1
		except:	
			pass
		return verified

	def index(self,uname=None,pword=None,redirect=0):
                loggedIn=0
                if uname!=None:
			cherrypy.session.clear()
                        lookup=list(c['data']['users'].find({'username':str(uname),'password':str(pword)}))
                        if len(lookup)==1:
				cherrypy.lib.sessions.init(name=str(uname))
                                print 'FOUND USER %s'%(str(lookup[0]['username']))
                                cherrypy.session['login']=str(uname)
                                loggedIn=1
                        else:
                                loggedIn=2
                output=''
                pageurl=webpageDirectory+'login.html'
                f=open(pageurl,'r')
                for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        elif 'name=content' in l:
                                output+=l
				if redirect: output+="<font color='red'> Please log in.</font><br>"
                                if loggedIn==1: output+='%s, you are logged in <br>'%(str(uname))
                                elif loggedIn==2: output+='<font color="red"> login failed.</font><br>'
                        else: output+=l
                return output
        index.exposed=True

        def create(self,uname=None,pword=None):
                userAdded=0
                if uname!=None:
                        c['data']['users'].insert({'username':str(uname),'password':str(pword)})
                        userAdded=1

                output=''
                pageurl=webpageDirectory+'login.html'
                f=open(pageurl,'r')
                for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        elif 'name=content' in l:
                                output+=l
                                if userAdded==1: output+='user: %s added.'%(str(uname))
                        else: output+=l
                return output
        create.exposed=True


	def load(self, musiclist=None):
		verified=self.verifyUser()
		if not verified: return self.index(redirect=1) 

                if musiclist!=None:
                        musiclist=str(musiclist)
                        print musiclist
                output=''
                f=open(webpageDirectory+'load.html','r')
                for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        elif 'name=content' in l:
                                output+=l
                                try: output+='Hello %s'%cherrypy.session['login']
                                except: pass

                        elif 'loadlist' in l:
                                if musiclist==None: continue
                                playlist=list(c['lists'][musiclist].find())
                                for i in range(len(playlist)):
                                        name=playlist[i]['song']
                                        artist=playlist[i]['artist']
                                        url=playlist[i]['url']

                                        output+="%d: <a href=%s>%s by %s</a>  <br>\n"%(i+1, url,name,artist)
                                        #for metadata in song:
                                                #print metadata
                                                #output+=str(metadata)
                        else: output+=l
                return output
        load.exposed=True

	def lists(self,listname=None,url=None,song=None,artist=None):
		verified=self.verifyUser()
                if not verified: return self.index(redirect=1) 

		added=0
		if listname!=None and url!=None and song!=None and artist!=None:
			listname,url,song,artist=str(listname),str(url),str(song),str(artist)
		
			#logic to add to mongo
			url=url.split('=')[0].split('?')[0]
			url="http://www.youtube.com/embed/%s"%(url)
			#verify that it's a real url

			
			c['lists'][listname].insert({'url':url,'song':song,'artist':artist})
			added=1

		output=''
		f=open(webpageDirectory+'lists.html','r')
		for l in f:
			if 'headergoeshere' in l: output+=header()
			elif 'footergoeshere' in l: output+=footer()
			elif "name=content" in l and added:
				output+=l
				output+='added '+song+' to '+listname+'!<br>'	
			else: output+=l
		return output
	lists.exposed=True
	
	def convert(self, url=None):
		verified=self.verifyUser()
                if not verified: return self.index(redirect=1)

		output=''
                f=open(webpageDirectory+'convert.html','r')
                for l in f:
			if "linkgoeshere" in l and url!=None:
				hashTag=url.strip('\n').strip('"').split('=')[1]
				link="<iframe width=300 height=301 src=http://www.youtube.com/embed/"+hashTag+"?rel=0&autoplay=1&modestbranding=1&autohide=0&#8243; frameborder=0></iframe><br>"
				output+=link
			elif 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
			else: output+=l
                return output
	convert.exposed = True


	

		


'''
class Template(object):
	def index(self):
		output=''
		pageurl=webpageDirectory+''
        	f=open(pageurl,'r')
		for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        else: output+=l
                return output
        index.exposed=True

class Posttest(object):
	def index(self,login=None):
		if login!=None:
			print 'test',str(login)
		output=''
		pageurl=webpageDirectory+'posttest.html'
        	f=open(pageurl,'r')
		for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        else: output+=l
                return output
        index.exposed=True
'''

	

root=Index()
#root.login=Login()
#root.posttest=Posttest()
#root.convert=Convert()
#root.lists=Lists()
#root.load=Load()
#root.session=Session()

cherrypy.config.update({'server.socket_host':'0.0.0.0',
			'server.socket_port':8080,
			'tools.sessions.on':True,
			#'tools.sessions.storage_type':"file",
			#'tools.sessions.storage_path':"/var/www/music/datadir/cherry_session",
			#'tools.sessions.timeout':60
			})
cherrypy.quickstart(root)
