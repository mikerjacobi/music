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



class Index(object):
	def verifyUser(self):
		verified=0
		try: 
			cherrypy.session['login']
			verified=1
		except:	
			pass
		return verified

	def player(self):
		try: 
			cherrypy.session['playlist']
			cherrypy.session['playlistOwner']
		except: return ''



		output=''
		f=open(webpageDirectory+'player.html','r')
		for l in f:
			if 'initialVideo:' in l:
				output+='initialVideo: songs[%s],\n'%(cherrypy.session['songNumber'])
			elif 'infogoeshere' in l:
				output+='<label id="songinfoLabel"> %s </label><br>\n'%("test")
			elif 'songsgohere' in l:
				try: 
					songIndex=0
					playlistName=cherrypy.session['playlist'].split('.')[1]
					currList=list(c[cherrypy.session['playlistOwner']][cherrypy.session['playlist']].find())
					for song in currList:
						youtubeID=song['url'].split('=')[-1]
						name=song['song']
						artist=song['artist']
						output+='songs[%d]="%s";\n'%(songIndex,youtubeID)
						output+='songText[%d]="%s by %s on playlist:%s";\n'%(songIndex,name,artist,playlistName)
						songIndex+=1
					output+='currSongIndex=%s;\n'%(cherrypy.session['songNumber'])
					output+='max=%d;\n'%(songIndex)
				except Exception, p:
					print 'PLAYER ERROR: ',str(p)
					pass
			else:
				output+=l
		return output
	player.exposed=True

	def index(self,t=0,playlistOwner=None,playlist=None,songNumber=0):
		cherrypy.session['songNumber']=str(songNumber)
                if playlist!=None and playlistOwner!=None:
                        cherrypy.session['playlist']='lists.'+str(playlist)
			cherrypy.session['playlistOwner']=str(playlistOwner)

		output=''
                f=open(webpageDirectory+'main.html','r').read().split('\n')
                for l in f:
			if 'loadpagegoeshere' in l:
				output+="<script type='text/javascript'> loadPage('%s'); </script>"%(str(t))
			else:
                        	output+=l
                return output
        index.exposed=True

	def testing(self):
                output=''
                f=open(webpageDirectory+'testing.html','r').read().split('\n')
                for l in f:
			output+=l
                return output
        testing.exposed=True	

	def mylists(self):
		verified=self.verifyUser()
                if not verified: return "please login"
		
                output=''
                f=open(webpageDirectory+'mylists.html','r').read().split('\n')
                for l in f:
			if 'viewlists' in l:
                                playlists=c[cherrypy.session['login']].collection_names()
                                if len(playlists)==0: output+="<b> None<br></b>"
                                else:
                                        #javascript="\n<script type='text/javascript'>\n var playlists={};\n"
                                        javascript='\nvar playlists={};\n'
                                        for playlist in playlists:
                                                if playlist=='system.indexes':continue
                                                playlist=playlist.split('.')[1]
                                                output+="<button onclick='viewPlaylist(\"%s\")'> <b>%s</b> </button> <div class='listData' id='%sDiv' > </div>\n"%(playlist,playlist,playlist)
                                                javascript+="playlists[\"%s\"]=\""%(playlist)
                                                songs=list(c[cherrypy.session['login']]["lists."+playlist].find())
                                                i=0
                                                for song in songs:
                                                        name=song['song']
                                                        artist=song['artist']
                                                        songid=song['url'].split('=')[1]
                                                        url="http://jacobra.com:8080?playlistOwner=%s&playlist=%s&songNumber=%d"%(cherrypy.session['login'],playlist,i)
                                                        #output+="\t %d: <a href=%s>%s by %s</a>  <br>\n"%(i+1, url,name,artist)
                                                        javascript+="\t %d: <a href=%s>%s by %s</a>  <br>"%(i+1, url,name,artist)
                                                        i+=1
                                                output+='<br>'
                                                javascript+="\";\n  "
                                        #javascript+="</script>\n\n<br>"
                                        #output+=javascript
                        elif 'javascriptgoeshere' in l:
                                #continue
                                output+=javascript
			else:
                        	output+=l
                return output
        mylists.exposed=True

	def listForm(self,listname=None,url=None,song=None,artist=None):
		pass
	listForm.expose=True


	def login(self):
                output=''
                f=open(webpageDirectory+'login.html','r').read().split('\n')
                for l in f:
			if 'messagetouser' in l:
				try:
					if cherrypy.session['login']!='': output+='You\'re logged in, %s!'%(cherrypy.session['login'])
				except: pass
			else:
                        	output+=l
                return output
        login.exposed=True
	
	#this is the logic called when users click login	
	def loginForm(self,uname=None,pword=None):
		try: del cherrypy.session['login']
		except: pass
		if uname!=None:
                        cherrypy.session.clear()
                        lookup=list(c['data']['users'].find({'username':str(uname),'password':str(pword)}))
                        if len(lookup)==1:
                                cherrypy.lib.sessions.init(name=str(uname))
                                cherrypy.session['login']=str(uname)
				return self.index(t=1)
			else:
				return self.index()
	loginForm.exposed=True

	#this is the logic called when users create a new account from the login screen
	def createForm(self,uname=None,pword=None):
		try: del cherrypy.session['login']
		except: pass
		if uname==None or pword==None: return self.index()
		uname,pword=str(uname),str(pword)
		lookup=list(c['data']['users'].find({'username':str(uname)}))
		if len(lookup)!=0: return self.index()
		c['data']['users'].insert({'username':uname,'password':pword})	
		cherrypy.session['login']=uname
		return self.index()
	createForm.exposed=True

		

		
	#####################3 end temp!!!!
		
			
	

root=Index()
cherrypy.tree.mount(root, '/static', config={'/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': '/var/www/music/static'}})

cherrypy.config.update({'server.socket_host':'0.0.0.0',
			'server.socket_port':8080,
			'tools.sessions.on':True,
			})

cherrypy.quickstart(root)











