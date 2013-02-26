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

class Load(object):
        def index(selfi, musiclist=None):
		if musiclist!=None:
			musiclist=str(musiclist)
			print musiclist
                output=''
                f=open(webpageDirectory+'load.html','r')
                for l in f:
                        if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
                        else: output+=l
                return output
        index.exposed=True
		

class Lists(object):
	def index(self,name=None,url=None):
		added=0
		if name!=None and url!=None:
			#logic to add to mongo
			c['lists'][str(name)].insert({'url':str(url)})
			added=1

		output=''
		f=open(webpageDirectory+'lists.html','r')
		for l in f:
			if 'headergoeshere' in l: output+=header()
			elif 'footergoeshere' in l: output+=footer()
			elif "name=content" in l and added:
				output+=l
				output+='added '+str(url)+' to '+str(name)+'!<br>'	
			else: output+=l
		return output
	index.exposed=True

class Convert(object):
	def index(self, url=None):
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
	index.exposed = True
	

class Index(object):
	def index(self):
		output=''
		f=open(webpageDirectory+'index.html','r')
		for l in f:
			if 'headergoeshere' in l: output+=header()
                        elif 'footergoeshere' in l: output+=footer()
			else: output+=l
		return output
	index.exposed = True


root=Index()
root.convert=Convert()
root.lists=Lists()
root.load=Load()

cherrypy.config.update({'server.socket_host':'0.0.0.0','server.socket_port':8080,'tools.sessions.on':True})
cherrypy.quickstart(root)
