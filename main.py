# coding: utf-8

from simpleplugin import Plugin

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, sys, re

import vsdbg
vsdbg.s._debug = False

import shikicore
import time

plugin = Plugin()

# ------ Cache requests -----------------

def request_limit(func, *args):
	t0 = time.time()
	res = func(*args)
	t1 = time.time()

	total = t1-t0

	#xbmc.log(str(total))

	if total < 0.2:
		time.sleep(0.2-total)

	return res

@plugin.mem_cached(30)
def shikicore_animes_(id):
	return request_limit(shikicore.animes_, id)

@plugin.mem_cached(30)
def shikicore_animes_roles(id):
	return request_limit(shikicore.animes_roles, id)

@plugin.mem_cached(30)
def shikicore_animes_similar(id):
	return request_limit(shikicore.animes_similar, id)

# ------ Actions -------------------------
@plugin.action()
def root(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'files')

	#flag = os.path.join(plugin.path, 'resources', 'flags', 'gp.png')

	return [{'label': u'Поиск', 'url': plugin.get_url(action='search')},
			{'label': u'Расширенный поиск', 'url': plugin.get_url(action='search_adv')},
			{'label': u'Онгоинг', 'url': plugin.get_url(action='ongoing')},
			{'label': u'По годам', 'url': plugin.get_url(action='by_year')},
			{'label': u'По жанрам', 'url': plugin.get_url(action='by_genre')},
	
			#{'label': 'test', 'url': plugin.get_url(action='test') }
	]

def year_item(year):
	return {'label': str(year), 'url': plugin.get_url(action='year', year=year)}

@plugin.action()
def by_year(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'files')

	import datetime
	now = datetime.datetime.now()

	return [ year_item(year) for year in xrange(now.year, 1990, -1) ]

def genre_item(genre):
	return { 'label': genre['russian'], 'url': plugin.get_url(action='genre', **genre) }

@plugin.action()
def by_genre(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'files')

	vsdbg._bp()

	listing = [ genre_item(genre) for genre in shikicore.genres() if genre['kind'] == 'anime' ]
	return Plugin.create_listing(listing, sort_methods=(xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
												   xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE))
def person(p):
	xbmc.log(str(p))
	return { 'name': p['character']['russian'], 'thumbnail': 'https://moe.shikimori.org' + p['character']['image']['original'] }

def _anime_item(o):
	xbmc.log(str(o))


	ams = shikicore_animes_(o['id'])
	roles = shikicore_animes_roles(o['id'])

	xbmc.log(str(ams))

	description = ams['description']
	if description:
		description = description.replace('[[', '')
		description = description.replace(']]', '')
		description = re.sub(r'\[.+?\]', '', description)

	infovideo = { 
			'title': o['russian'],
			'genre': ', '.join([item['russian'].lower() for item in ams['genres']]), 
			'originaltitle': ams['name'],
			'year': ams['aired_on'].split('-')[0],
			'mpaa': ams['rating'],
			'rating': ams['score'],
			'duration': str(ams['duration']),
			'studio': ', '.join([item['name'] for item in ams['studios']]),
			'plot': description }

	info = {'label': o['russian'], 
			'info': {'video': infovideo },
			'thumb': 'https://moe.shikimori.org' + o['image']['original'], 
			'url': plugin.get_url(action='play', id=o['id']),
			'fanart': 'https://moe.shikimori.org' + ams['screenshots'][0]['original'] if ams['screenshots'] else None,
			'cast': [person(item) for item in roles if item.get('character')]}

	return info


def anime_item(o):

	similar_url = plugin.get_url(action='similar', id=o['id'])
	xbmc.log(similar_url)

	_ai = _anime_item(o)

	li = plugin.create_list_item(_ai)
	li.addContextMenuItems([(u'Подобные', 'Container.Update("%s")' % similar_url,)])

	return {'list_item': li, 'url': _ai['url']}

def next_item(params, page):
	params['page'] = page

	import urllib
	command = sys.argv[0] + '?' + urllib.urlencode(params)
	return { 'label': '[Next page]', 'url': command, 'is_folder': True }

@plugin.action()
def test(params):
	vsdbg._bp()
	items = []
	for i in range(100):
		items.append({'label': str(i), 'url': plugin.get_url(action='none')})
		xbmc.sleep(1000)
		if xbmc.abortRequested:
			break
	return items

@plugin.action()
def ongoing(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	vsdbg._bp()

	page = int(params.get('page', 1))

	oo = shikicore.ongoing(limit=10, page=page)
	res = [ anime_item(o) for o in oo]

	if res:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def year(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	vsdbg._bp()

	page = int(params.get('page', 1))

	oo = shikicore.by_year(params['year'], limit=10, page=page)
	res = [ anime_item(o) for o in oo]

	if res:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def genre(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	page = int(params.get('page', 1))

	oo = shikicore.by_genre(params['id'], limit=10, page=page)
	res = [ anime_item(o) for o in oo]

	if res:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def similar(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	oo = shikicore_animes_similar(params['id'])
	return [ anime_item(o) for o in oo]

@plugin.action()
def search(params):
	return []

@plugin.action()
def search_adv(params):
	return []

@plugin.action()
def play(params):
	pass

#vsdbg._bp()

uname = plugin.get_setting('username')
passw = plugin.get_setting('password')
token = plugin.get_setting('token')

uname_ok = plugin.get_setting('username_ok')
passw_ok = plugin.get_setting('password_ok')

xbmc.log(uname)
xbmc.log(passw)

if uname == uname_ok and passw == passw_ok and token:
	r = shikicore.authorize(uname, passw, token)
else:
	r = shikicore.authorize(uname, passw)
plugin.log_error(str(r))

if not r:
	plugin.addon.openSettings()
else:
	plugin.set_setting('token', r)
	plugin.set_setting('username_ok', uname)
	plugin.set_setting('password_ok', passw)

	plugin.run()