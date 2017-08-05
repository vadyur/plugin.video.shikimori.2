# coding: utf-8

from simpleplugin import Plugin

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, sys, re, json

import vsdbg
#vsdbg.s._debug = False

import time
import urllib
import shikicore

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

@plugin.mem_cached(30)
def shikicore_animes_related(id):
	return request_limit(shikicore.animes_related, id)

@plugin.mem_cached(30)
def shikicore_whoami():
	return shikicore.whoami()

# ------ Actions -------------------------
@plugin.action()
def root(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'files')

	#flag = os.path.join(plugin.path, 'resources', 'flags', 'gp.png')

	return [{'label': u'Поиск', 'url': plugin.get_url(action='search')},
			{'label': u'Расширенный поиск', 'url': plugin.get_url(action='search_adv')},
			{'label': u'По годам', 'url': plugin.get_url(action='by_year')},
			{'label': u'По жанрам', 'url': plugin.get_url(action='by_genre')},
			{'label': u'Избранное', 'url': plugin.get_url(action='favourites')},
			{'label': u'Списки', 'url': plugin.get_url(action='rates')},
			{'label': u'Онгоинг', 'url': plugin.get_url(action='ongoing')},
	
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

	#vsdbg._bp()

	listing = [ genre_item(genre) for genre in shikicore.genres() if genre['kind'] == 'anime' ]
	return Plugin.create_listing(listing, sort_methods=(xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
												   xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE))
def person(p):
	xbmc.log(str(p))
	return { 'name': p['character']['russian'], 'thumbnail': 'https://moe.shikimori.org' + p['character']['image']['original'] }

def play_url(o):

	#vsdbg._bp()

	try:
		xbmcaddon.Addon('plugin.video.shikimori.org')
		url = 'https://play.shikimori.org' + o['url']
		return 'plugin://plugin.video.shikimori.org/?' + urllib.urlencode({
			'url': str(url), 'mode': 'FILMS'
		})
	except:
		return plugin.get_url(action='play', **o)

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
			'title': ams['russian'],
			'genre': ', '.join([item['russian'].lower() for item in ams['genres']]), 
			'originaltitle': ams['name'],
			'year': ams['aired_on'].split('-')[0],
			'mpaa': ams['rating'],
			'rating': ams['score'],
			'duration': str(ams['duration']),
			'studio': ', '.join([item['name'] for item in ams['studios']]),
			'plot': description }

	info = {'label': ams['russian'], 
			'info': {'video': infovideo },
			'thumb': 'https://moe.shikimori.org' + ams['image']['original'], 
			'fanart': 'https://moe.shikimori.org' + ams['screenshots'][0]['original'] if ams['screenshots'] else None,
			'cast': [person(item) for item in roles if item.get('character')]}

	info['url'] =  plugin.get_url(action='play', thumb = info['thumb'], fanart=info['fanart'], **o)

	return info


def anime_item(o):

	similar_url = plugin.get_url(action='similar', id=o['id'])
	related_url = plugin.get_url(action='related', id=o['id'])
	rate_url	= plugin.get_url(action='rate', id=o['id'])
	xbmc.log(similar_url)

	_ai = _anime_item(o)
	menu_items = [(u'Подобные', 'Container.Update("%s")' % similar_url,),
				  (u'Связанные','Container.Update("%s")' % related_url,),
				  (u'Добавить в список', 'RunPlugin("%s")' % rate_url),
				 ]
	if 'FILMS' in _ai['url']:
		menu_items.append((u'Смотреть оригинальным плагином', 'Container.Update("%s")' % _ai['url'],))

	li = plugin.create_list_item(_ai)
	li.addContextMenuItems(menu_items)

	o['_ai'] = _ai
	o['similar_url'] = similar_url
	o['related_url'] = related_url
	o['rate_url']	 = rate_url

	return {'list_item': li, 'url': _ai['url']}

@plugin.action()
def anime_adv(params):
	o = json.loads(params['o'])
	return [
		anime_item(o),
		{'label': u'Подобные', 'url': o['similar_url']},	
		{'label': u'Связанные','url': o['related_url']},
		{'label': u'Добавить в список', 'url': o['rate_url']}
	]

def anime_catalog(o):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	return {'label': o['russian'], 
			'icon': 'https://moe.shikimori.org' + o['image']['preview'], 
			'thumb': 'https://moe.shikimori.org' + o['image']['original'], 
			'url': plugin.get_url(action='anime_adv', o=json.dumps(o))}

def next_item(params, page):
	params['page'] = page

	command = sys.argv[0] + '?' + urllib.urlencode(params)
	return { 'label': u'[Далее]', 'url': command, 'is_folder': True }

@plugin.action()
def test(params):
	#vsdbg._bp()
	items = []
	for i in range(100):
		items.append({'label': str(i), 'url': plugin.get_url(action='none')})
		xbmc.sleep(1000)
		if xbmc.abortRequested:
			break
	return items

@plugin.action()
def favourites(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	page = int(params.get('page', 1))

	vsdbg._bp()

	oo = shikicore.favourites(limit=50, page=page)
	res = [ anime_catalog(o) for o in oo]

	if res and len(res) == 50:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def ongoing(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	#vsdbg._bp()

	page = int(params.get('page', 1))

	oo = shikicore.ongoing(limit=50, page=page)
	res = [ anime_catalog(o) for o in oo]

	if res and len(res) == 50:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def year(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	#vsdbg._bp()

	page = int(params.get('page', 1))

	oo = shikicore.by_year(params['year'], limit=50, page=page)
	res = [ anime_catalog(o) for o in oo]

	if res and len(res) == 50:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def genre(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	#vsdbg._bp()

	page = int(params.get('page', 1))

	oo = shikicore.by_genre(params['id'], limit=50, page=page)
	res = [ anime_catalog(o) for o in oo]

	if res and len(res) == 50:
		res.append(next_item(params, page+1))

	return res

@plugin.action()
def similar(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	oo = shikicore_animes_similar(params['id'])
	return [ anime_item(o) for o in oo]

@plugin.action()
def related(params):
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	oo = shikicore_animes_related(params['id'])

	return [ anime_item(o['anime']) for o in oo if o.get('anime')]

@plugin.action()
def search(params):
	dlg = xbmcgui.Dialog()
	s = params.get('search')
	if not s:
		s = dlg.input(u'Введите поисковую строку')
		command = sys.argv[0] + sys.argv[2] + '&search=' + urllib.quote(s)
		xbmc.executebuiltin(b'Container.Update(\"%s\")' % command)
		return

	oo = shikicore.animes_search(s)
	return [ anime_item(o) for o in oo]

@plugin.action()
def search_adv(params):
	return [{'label': u'Годы', 'url': plugin.get_url(action='f_years')},
			{'label': u'Жанры', 'url': plugin.get_url(action='f_genres')},
			{'label': u'Рейтинг', 'url': plugin.get_url(action='f_score')},	]

@plugin.action()
def f_years(params):
	pass

@plugin.action()
def f_genres(params):
	pass

@plugin.action()
def f_score(params):
	pass

def get_list(dirPath):
	_listdircmd = '{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"properties": ["file", "title"], "directory":"%s", "media":"files"}, "id": "1"}'
	itmList = eval(xbmc.executeJSONRPC(_listdircmd % (dirPath)))['result']['files']
	return itmList

def src_item(s):
	return { 'label': s['label'], 'url': s['file'], 'is_playable': True }	

@plugin.action()
def sources(params):
	vsdbg._bp()
	l = get_list(params['cmd'])

	return [ src_item(s) for s in l ]

def episode_item(e):
	return {
		'label': e['label'],
		'url': plugin.get_url(action='sources', cmd=e['file'])
	}

@plugin.action()
def play(params):
	vsdbg._bp()

	options = []
	actions = []

	if xbmc.getCondVisibility("System.HasAddon(plugin.video.shikimori.org)"):
		def play_shiki():
			url = play_url(params)
			l = get_list(url)
			return [ episode_item(e) for e in l ]
		actions.append(play_shiki)
		options.append(u'Играть оригинальным плагином')

	if xbmc.getCondVisibility("System.HasAddon(script.media.aggregator)"):
		def act():
			cmd = 'plugin://script.media.aggregator/?' + urllib.urlencode(
				{'action': 'add_media',
				 'title': params['name'],
				 'imdb': 'sm' + params['id']})
			xbmc.executebuiltin('Container.Update("%s")' % cmd)
		actions.append(act)
		options.append(u'Перейти/добавить в медиатеку')

	res = None
	if options:
		if len(options) == 1:
			res = actions[0]()
		else:
			index = xbmcgui.Dialog().contextmenu(list=options)
			if index >= 0:
				res = actions[index]()
	if res:
		return res


@plugin.action()
def rate(params):
	vsdbg._bp()

	id = params['id']

	from src.rates import context_menu
	context_menu(id, shikicore_whoami()['id'])


@plugin.action()
def rates(params):
	vsdbg._bp()

	from src.rates import status_list
	return status_list(shikicore_whoami()['id'], plugin)


@plugin.action()
def rate_list(params):
	vsdbg._bp()

	Ids = params['ids'].split(',')

	curr_ids = Ids[:10]
	next_ids = Ids[10:]

	result = [ anime_item({'id': id }) for id in curr_ids ]

	if next_ids:
		params['ids'] = ','.join(next_ids)
		command = plugin.get_url(**params)
		result.append({'label': u'[Далее]', 'url': command, 'is_folder': True})

	return result


#vsdbg._bp()
if __name__ == '__main__':
	shikicore.api = shikicore.authorize_me()
	if shikicore.api:
		plugin.run()
