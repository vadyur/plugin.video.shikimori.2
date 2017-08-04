# -*- coding: utf-8 -*-

import xbmc, sys, json

xbmc.log(repr(sys.argv))

class Main():
	def __init__(self):

		if 'synclibrary' in sys.argv:
			self.synclibrary()

	def synclibrary(self):
		req = {	"jsonrpc": "2.0", 
				"method": "VideoLibrary.GetTVShows", 
				"params": {
					"filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, 
					"properties": ["title", "originaltitle", "year", "file", "imdbnumber", "playcount"]
				}, 
				"id": "876"}
		result = json.loads(xbmc.executeJSONRPC(json.dumps(req)))
		try:
			for r in result['result']['tvshows']:
				if 'Anime' in r['file']:
					xbmc.log('{0}: {1}'.format(r['title'].encode('utf-8'), r['playcount']))
		except KeyError:
			xbmc.log('KeyError: Animes not found')
		


Main()