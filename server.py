import cherrypy
from pymongo import *

webpageDirectory="pages/"
c=Connection()

class Lists(object):
	def index(self,name=None):
		if name!=None:
			cherrypy.lib.sessions['name']=name
		output=''
		f=open(webpageDirectory+'lists.php','r')
		for l in f:
			output+=l
		return output
	index.exposed=True

class Convert(object):
	def index(self, url=None):
		output=''
                f=open(webpageDirectory+'convert.php','r')
                for l in f:
			if "linkgoeshere" in l and url!=None:
				hashTag=url.strip('\n').strip('"').split('=')[1]
				link="<iframe width=300 height=301 src=http://www.youtube.com/embed/"+hashTag+"?rel=0&autoplay=1&modestbranding=1&autohide=0&#8243; frameborder=0></iframe>\n"
				output+=link
			else:
                        	output+=l
		try: output+='name=',cherrypy.lib.sessions['name']
		except: pass
                return output
	index.exposed = True
	

class Index(object):
	def index(self):
		output=''
		f=open(webpageDirectory+'index.php','r')
		for l in f:
			output+=l
		return output
	index.exposed = True


root=Index()
root.convert=Convert()
root.lists=Lists()

cherrypy.config.update({'server.socket_host':'0.0.0.0','server.socket_port':8080,'session_filter.on':True})
cherrypy.quickstart(root)
