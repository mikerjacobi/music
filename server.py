#!/usr/bin/python
import cherrypy
from pymongo import *
import os
import time
import random
import datetime

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
					playlistName=sesh['playlist']
					currList=list(c['music']['playlists'].find({'listname':sesh['playlist'],'author':sesh['author']}))[0]
					currSongs=currList.get('songs')
					for song in currSongs:
						songData=list(c['music']['songs'].find({'url':str(song)}))[0]
						#youtubeID=song['url'].split('=')[-1]
						songid=str(song)
						name=songData.get('songname')
						artist=songData.get('artist')
						output+='songs[%d]="%s";\n'%(songIndex,songid)
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

	def edit(self,listname=None):
		try: 
			data={}
			data['author']=sesh['currUser']
			data['listname']=sesh['editlist']
		except: return self.index(t=3)
		output=''
                f=open(webpageDirectory+'edit.html','r')
		songs={}
		for l in f:
			if 'editgoeshere' in l:
				output+="<h4 align='left'>playlist: %s </h4>(<a  href='/index?t=2' onclick='removePlaylist()'>delete playlist</a>)<br>"%(sesh['editlist'])
				data=list(c['music']['playlists'].find(data))[0]
				template='%s: <input id="%s" type="text" value="%s"></input>\n<br>'
				output+=template%('genre 1',data['g1'],data['g1'])
				output+=template%('genre 2',data['g2'],data['g2'])
				output+=template%('vibe 1',data['v1'],data['v1'])
				output+=template%('vibe 2',data['v2'],data['v2'])
				output+=template%('vibe 3',data['v3'],data['v3'])

				songs=data['songs']
			elif 'songgoeshere' in l:
				i=1
				output+='<h4>songs: </h4>'
				for song in songs.keys():
					songData=list(c['music']['songs'].find({'url':song}))[0]		
					output+="%d: %s by %s (<a href='/index?t=4&editlist=%s' onclick='removeSong(\"%s\")'>remove</a>)<br>\n"%(i,songData['songname'],songData['artist'],sesh['editlist'],str(song))
					i+=1
				 
			else:
				output+=l
		return output
	edit.exposed=True

	def discover(self, query=None):

		#process the query
		useQuery=0
		if query!=None:
			sesh['query']=str(query)
			if sesh['query']!='': useQuery=1
		else:
			try: 
				sesh['query']
				if sesh['query']=='':userQuery=0
				else:useQuery=1
			except: pass

		if useQuery: print '!!!!!!!!!!!!!',sesh['query']

		output=''
		f=open(webpageDirectory+'discover.html').read().split('\n')
		for l in f:
			if 'discovergoeshere' in l:
				if useQuery==0:	
					i,numPlaylists=0,5
					playlists=list(c['music']['playlists'].find())
					displayLists={}
					while len(displayLists)<numPlaylists:
						playlist=playlists[random.randint(0,numPlaylists-1)]		
						listID=playlist.get('_id')
						try: displayLists[listID] #check to see if we have this playlist
						except:
							listname=playlist.get('listname')
							author=playlist.get('author')
							html='%d: <a href="%s?t=1&author=%s&playlist=%s">%s by %s</a><br>\n'%(i+1,webRoot,author,listname,listname,author)	
							displayLists[listID]=1
							output+=html
			
						
						i+=1
					pass
				else:
					output+=sesh['query']
			else:
				output+=l
		return output
	discover.exposed=True

	def index(self,t=1,author=None,playlist=None,songNumber=0,editlist=None):
		sesh['songNumber']=str(songNumber)
                if playlist!=None and author!=None:
                        sesh['playlist']=str(playlist)
			sesh['author']=str(author)
		if editlist!=None: sesh['editlist']=str(editlist)

		output=''
                f=open(webpageDirectory+'main.html','r').read().split('\n')
                for l in f:
			if 'loadpagegoeshere' in l:
				output+="<script type='text/javascript'> loadPage('%s'); </script>"%(str(t))
			else:
                        	output+=l
                return output
        index.exposed=True

	def incrementSong(self,songURL=None):
		if songURL!=None:
			c['music']['songs'].update({'url':str(songURL)},{'$inc':{'numListens':1}})
			currPlaylist={}
			currPlaylist['author']=sesh['author']
			currPlaylist['listname']=sesh['playlist']
			c['music']['playlists'].update(currPlaylist,{'$inc':{'totalSongListens':1, 'songs.%s'%songURL:1}})
	incrementSong.exposed=True

	def removePlaylist(self):
		c['music']['playlists'].remove({'author':sesh['currUser'],'listname':sesh['editlist']})
	removePlaylist.exposed=True

	def removeSong(self, url=None):
		if url!=None:
			url=str(url)
			c['music']['playlists'].update({'author':sesh['currUser'],'listname':sesh['editlist']},{'$unset':{'songs.%s'%url:1}})
	removeSong.exposed=True

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
					output+="No playlist selected!\n<br>"
					output+="<a href='/index?t=0'>Discover</a> a playlist or <a href='/index?t=2'>Make</a> your own!"
					return output
				output+="<h4>playlist: %s, by user: %s</h4>\n"%(sesh['playlist'], sesh['author'])
				#songs=list(c[sesh['author']][sesh['playlist']].find())
				currList=list(c['music']['playlists'].find({'listname':sesh['playlist'],'author':sesh['author']}))[0]
                                currSongs=currList.get('songs')
				i=1
				for song in currSongs:
					songData=list(c['music']['songs'].find({'url':str(song)}))[0]
					name=songData.get('songname')
                                        artist=songData.get('artist')
					output+="\t %d: %s by %s<br>\n"%(i,name,artist)
					i+=1
				
			else:
				output+=l
		return output
	playing.exposed=True

	def mylists(self):
		verified=self.verifyUser()
                if not verified: return "<h2>CREATE</h2> You need to <a href='#' onclick=\"loadPage('3');\">Login</a> to see your playlists!"

		
                output=''
                f=open(webpageDirectory+'mylists.html','r').read().split('\n')
		listnames=[]
                for l in f:
			if 'viewlists' in l:
                                #playlists=c[sesh['currUser']].collection_names()
				playlists=list(c['music']['playlists'].find({'author':sesh['currUser']}))
                                if len(playlists)==0: output+="<b> None<br></b>"
                                else:
                                        #javascript="\n<script type='text/javascript'>\n var playlists={};\n"
                                        javascript='\nvar playlists={};\n'
                                        for playlist in playlists:
                                                #if playlist=='system.indexes':continue
                                                #playlist=playlist.split('.')[1]
						playlistName=playlist['listname']
						listnames.append(playlistName)
                                                #output+="<button onclick='viewPlaylist(\"%s\")'> <b>%s</b> </button> <div class='listData' id='%sDiv' > </div>\n"%(playlistName,playlistName,playlistName)
						view="<label onclick='viewPlaylist(\"%s\")'> (view) </label>\n"%(playlistName)
						edit='(<a href="/index?t=4&editlist=%s">edit</a>)\n'%(playlistName)
						play="http://jacobra.com:8080?t=1&author=%s&playlist=%s"%(sesh['currUser'],playlistName)
						#output+="<label onclick='viewPlaylist(\"%s\")'> <b>%s</b> </label> %s %s <div class='listData' id='%sDiv' > </div>\n"%(playlistName,playlistName,view,edit,playlistName)
						output+="<a href='%s'> <b>%s</b> </a> %s %s <div class='listData' id='%sDiv' > </div>\n"%(play,playlistName,view,edit,playlistName)
                                                javascript+="playlists[\"%s\"]=\""%(playlistName)
                                                #songs=list(c[sesh['currUser']]["lists."+playlist].find())
						songs=playlist['songs']
                                                i=0
						print songs
                                                for song in songs.keys():
							playcount=songs[song]
							songData=c['music']['songs'].find({'url':str(song)})[0]
                                                        name=songData.get('songname')
                                                        artist=songData.get('artist')
                                                        songid=str(song)
                                                        url="http://jacobra.com:8080?t=1&author=%s&playlist=%s&songNumber=%d"%(sesh['currUser'],playlistName,i)
                                                        #output+="\t %d: <a href=%s>%s by %s</a>  <br>\n"%(i+1, url,name,artist)
                                                        javascript+="\t %d: <a height='auto' href=%s>%s by %s</a>  (%d)<br>"%(i+1, url,name,artist,playcount)
                                                        i+=1
                                                output+='<br>'
                                                javascript+="\";\n  "
                                        #javascript+="</script>\n\n<br>"
                                        #output+=javascript
                        elif 'javascriptgoeshere' in l:
                                #continue
                                try: output+=javascript
				except: pass
			elif 'listdropdown' in l:
				output+='listname: <select id=\"listname\">\n<br>'
				for playlist in listnames:
					output+="<option value='%s'>%s</option>\n<br>"%(playlist,playlist)
				output+="</select>\n<br>"
			else:
                        	output+=l
                return output
        mylists.exposed=True

	def listForm(self,listname=None,url=None,song=None,artist=None):
		if listname!=None and url!=None and song!=None and artist!=None:
                        listname,url,song,artist=str(listname),str(url),str(song),str(artist)
                        c[sesh['currUser']]['lists'][listname].insert({"url":url,"song":song,"artist":artist})
			songID=c['music']['songs'].update({'url':url},
				{'name':song,'artist':artist,'dateFirstAdded':str(datetime.datetime.now()),'numListens':0,'numAdds':0},
				upsert=True)
			#playlistID=c['music']['playlists'].insert({'listname':listname,'author':sesh['currUser'],'songs':[],'upvotes':0,'downvotes':0,'totalSongListens':0,'playlistStarts':0,'dateCreated':str(datetime.datetime.now()),'g1':'','g2':'','v1':'','v2':'','v3':''})
			
		
		return self.index(t=1)
	listForm.exposed=True

	def addToList(self,listname=None,song=None,artist=None,url=None):
		if listname==None or url==None or song==None or artist==None: return self.index(t=2)
		listname,url,song,artist=str(listname),str(url).split('=')[1],str(song),str(artist)
		newSong={'url':url}
		newSong['songname']=song
		newSong['artist']=artist
		newSong['dateFirstAdded']=str(datetime.datetime.now())
		newSong['numListens']=0
		newSong['numAdds']=0
		songID=c['music']['songs'].update({'url':url},newSong,upsert=True)
		c['music']['playlists'].update({'listname':listname,'author':sesh['currUser']},
			{'$set':{'songs.%s'%url:0}})	
		return self.index(t=2)
	addToList.exposed=True
	

	def createList(self,listname=None,g1=None,g2=None,v1=None,v2=None,v3=None):
                if not self.verifyUser(): return self.index(t=3)
		if listname==None: return self.index(t=2) 
		newList={'listname':str(listname)}
		newList['author']=sesh['currUser']
		newList['songs']={}
		newList['upvotes']=0
		newList['downvotes']=0
		newList['totalSongListens']=0
		newList['playlistStarts']=0
		newList['dateCreated']=str(datetime.datetime.now())
		if g1!=None: newList['g1']=str(g1)
		if g2!=None: newList['g2']=str(g2)
		if v1!=None: newList['v1']=str(v1)
		if v2!=None: newList['v2']=str(v2)
		if v3!=None: newList['v3']=str(v3)
		playlistID=c['music']['playlists'].insert(newList)
		return self.index(t=2)
	createList.exposed=True


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
		print 1
		if uname!=None:
                        sesh.clear()
                        #lookup=list(c['data']['users'].find({'username':str(uname),'password':str(pword)}))
                        lookup=list(c['music']['users'].find({'username':str(uname),'password':str(pword)}))
			print 2
                        if len(lookup)==1:
                                cherrypy.lib.sessions.init(name=str(uname))
                                sesh['currUser']=str(uname)
				print 3
				return self.index(t=2)
			else:
				print 4
				return self.index()
	loginForm.exposed=True

	#this is the logic called when users create a new account from the login screen
	def createForm(self,uname=None,pword=None):
		try: 
			del sesh['currUser']
		except: 
			pass
			
		if uname==None or pword==None: return self.index()
		uname,pword=str(uname),str(pword)
		lookup=list(c['music']['users'].find({'username':str(uname)}))
		if len(lookup)!=0: return self.index()
		c['data']['users'].insert({'username':uname,'password':pword})	
		c['music']['users'].insert({'username':uname,'password':pword,'dateAdded':str(datetime.datetime.now()),'playlists':{},'score':0})
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











