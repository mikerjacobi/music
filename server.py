#!/usr/bin/python
import cherrypy
from pymongo import *
import os
import time
import random

#boot up mongo
os.system('(mongod --dbpath datadir > datadir/log.txt) &')
time.sleep(1)
webRoot='http://jacobra.com:8080/'
webpageDirectory="pages/"
c=Connection()
cherrypy.lib.sessions.init()
sesh=cherrypy.session

class Index(object):
	def verifyUser(self):
		verified=0
		try: 
			sesh['currUser']
			verified=1
		except Exception, p:	
			pass
		return verified

	def player(self):
		try: 
			sesh['playlist']
			sesh['author']
		except: return ''



		output=''
		f=open(webpageDirectory+'player.html','r')
		for l in f:
			if 'initialVideo:' in l:
				output+='initialVideo: songs[%s],\n'%(sesh['songNumber'])
			elif 'infogoeshere' in l:
				output+='<label id="songinfoLabel"> %s </label><br>\n'%("test")
			elif 'songsgohere' in l:
				try: 
					songIndex=0
					playlistName=sesh['playlist'].split('.')[1]
					currList=list(c[sesh['author']][sesh['playlist']].find())
					for song in currList:
						youtubeID=song['url'].split('=')[-1]
						name=song['song']
						artist=song['artist']
						output+='songs[%d]="%s";\n'%(songIndex,youtubeID)
						output+='songText[%d]="%s <br> %s <br> playlist: %s";\n'%(songIndex,name,artist,playlistName)
						songIndex+=1
					output+='currSongIndex=%s;\n'%(sesh['songNumber'])
					output+='max=%d;\n'%(songIndex)
				except Exception, p:
					print 'PLAYER ERROR: ',str(p)
					pass
			else:
				output+=l
		return output
	player.exposed=True

	def discover(self, query=None):
		output=''
		f=open(webpageDirectory+'discover.html').read().split('\n')
		for l in f:
			if 'discovergoeshere' in l:
				continue
				dbs=list(c.database_names())
				for i in range(len(dbs)):dbs[i]=str(dbs[i])
				dbs.remove('data')
				dbs.remove('lists')
				if query==None:	
					i,numPlaylists=0,10
					while i<numPlaylists:
						try:
							author=str(dbs[random.randint(0,len(dbs)-1)])
							playlists=list(c[author].collection_names())
						except: continue
						try:
							for j in range(len(playlists)):playlists[j]=str(playlists[j])
						except:continue
						try:playlists.remove('system.indexes')
						except: pass
						try:playlist=playlists[random.randint(0,len(playlists)-1)].split('.')[1]
						except: playlist=playlists[random.randint(0,len(playlists)-1)]
						output+='<a href="%s?t=1&author=%s&playlist=%s">%s by %s</a><br>\n'%(webRoot,author,playlist,playlist,author)
						i+=1
					pass
				else:
					query=str(query)
			else:
				output+=l
		return output
	discover.exposed=True

	def index(self,t=1,author=None,playlist=None,songNumber=0):
		sesh['songNumber']=str(songNumber)
                if playlist!=None and author!=None:
                        sesh['playlist']='lists.'+str(playlist)
			sesh['author']=str(author)

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
	
	def playing(self):
		output=''
		f=open(webpageDirectory+'currPlaylist.html','r').read().split('\n')
		for l in f:
			if 'playinggoeshere' in l:
				try: 
					sesh['playlist']
					sesh['author']
				except: 
					output+="No playlist selected!\n"
					return self.index(t=0)
					continue
				output+="<h4>playlist: %s, by user: %s</h4>\n"%(sesh['playlist'].split('.')[1], sesh['author'])
				songs=list(c[sesh['author']][sesh['playlist']].find())
				i=1
				for song in songs:
					name=song['song']
                                        artist=song['artist']
					output+="\t %d: %s by %s<br>\n"%(i,name,artist)
					i+=1
				
			else:
				output+=l
		return output
	playing.exposed=True

	def mylists(self):
		verified=self.verifyUser()
                if not verified: return "<h2>CREATE</h2><a href='/index?t=3'> Please Login </a>"
		
                output=''
                f=open(webpageDirectory+'mylists.html','r').read().split('\n')
                for l in f:
			if 'viewlists' in l:
                                playlists=c[sesh['currUser']].collection_names()
                                if len(playlists)==0: output+="<b> None<br></b>"
                                else:
                                        #javascript="\n<script type='text/javascript'>\n var playlists={};\n"
                                        javascript='\nvar playlists={};\n'
                                        for playlist in playlists:
                                                if playlist=='system.indexes':continue
                                                playlist=playlist.split('.')[1]
                                                output+="<button onclick='viewPlaylist(\"%s\")'> <b>%s</b> </button> <div class='listData' id='%sDiv' > </div>\n"%(playlist,playlist,playlist)
                                                javascript+="playlists[\"%s\"]=\""%(playlist)
                                                songs=list(c[sesh['currUser']]["lists."+playlist].find())
                                                i=0
                                                for song in songs:
                                                        name=song['song']
                                                        artist=song['artist']
                                                        songid=song['url'].split('=')[1]
                                                        url="http://jacobra.com:8080?t=1&author=%s&playlist=%s&songNumber=%d"%(sesh['currUser'],playlist,i)
                                                        #output+="\t %d: <a href=%s>%s by %s</a>  <br>\n"%(i+1, url,name,artist)
                                                        javascript+="\t %d: <a height='auto' href=%s>%s by %s</a>  <br>"%(i+1, url,name,artist)
                                                        i+=1
                                                output+='<br>'
                                                javascript+="\";\n  "
                                        #javascript+="</script>\n\n<br>"
                                        #output+=javascript
                        elif 'javascriptgoeshere' in l:
                                #continue
                                try: output+=javascript
				except: pass
			else:
                        	output+=l
                return output
        mylists.exposed=True

	def listForm(self,listname=None,url=None,song=None,artist=None):
		if listname!=None and url!=None and song!=None and artist!=None:
                        listname,url,song,artist=str(listname),str(url),str(song),str(artist)
                        c[sesh['currUser']]['lists'][listname].insert({"url":url,"song":song,"artist":artist})
		
		return self.index(t=1)
	listForm.exposed=True


	def login(self):
                output=''
                f=open(webpageDirectory+'login.html','r').read().split('\n')
                for l in f:
			if 'messagetouser' in l:
				try:
					if sesh['currUser']!='': output+='You\'re logged in, %s!'%(sesh['currUser'])
				except: pass
			else:
                        	output+=l
                return output
        login.exposed=True

	def logout(self):
		for k in sesh.keys():
			del sesh[k]
		return self.index(t=3)
	logout.exposed=True
	
	#this is the logic called when users click login	
	def loginForm(self,uname=None,pword=None):
		try: del sesh['currUser']
		except: pass
		if uname!=None:
                        sesh.clear()
                        lookup=list(c['data']['users'].find({'username':str(uname),'password':str(pword)}))
                        if len(lookup)==1:
                                cherrypy.lib.sessions.init(name=str(uname))
                                sesh['currUser']=str(uname)
				return self.index(t=2)
			else:
				return self.index()
	loginForm.exposed=True

	#this is the logic called when users create a new account from the login screen
	def createForm(self,uname=None,pword=None):
		try: del sesh['currUser']
		except: pass
		if uname==None or pword==None: return self.index()
		uname,pword=str(uname),str(pword)
		lookup=list(c['data']['users'].find({'username':str(uname)}))
		if len(lookup)!=0: return self.index()
		c['data']['users'].insert({'username':uname,'password':pword})	
		sesh['currUser']=uname
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











