# coding: utf-8

import shikicore
import xbmc, xbmcgui

rate_statuses = ('completed',	 'dropped',		 'on_hold',		 'planned',			 'rewatching',		 'watching')
status_names = (u'Просмотрено',	u'Брошено',		u'Отложено',	u'Запланировано',	u'Пересматриваю',	u'Смотрю')

score_statuses =  {"0":u"Без оценки","1":u"Хуже некуда","2":u"Ужасно","3":u"Очень плохо","4":u"Плохо","5":u"Более-менее","6":u"Нормально","7":u"Хорошо","8":u"Отлично","9":u"Великолепно","10":u"Эпик вин!"}

def context_menu_rates(id, user_id):

	options = [u'Ничего не выбрано'] + list(status_names)
	actions = ['nothing'] + list(rate_statuses)

	#import vsdbg; vsdbg._bp()
	
	rates = shikicore.user_rates(user_id=user_id, target_id=id)
	xbmc.log(str(rates))
	
	if rates:
		r = rates[0]
		i = actions.index(r['status'])
		if i > 0:
			options[i] = u'[COLOR yellow][B] * ' + options[i] + ' * [/B][/COLOR]'
	else:
		options[0] = u'[COLOR yellow][B] * ' + options[0] + ' * [/B][/COLOR]'
	
	index = xbmcgui.Dialog().contextmenu(list=options)
	if index >= 0:
		status = actions[index]
	
		if rates:
			if index == 0:
				shikicore.delete_user_rate(r['id'])
			else:
				shikicore.update_user_rate(r['id'], status=status)
		elif index > 0:
			shikicore.create_user_rate(status=status, user_id=user_id, target_id=id)


def context_menu_scores(id, user_id):

	#import vsdbg; vsdbg._bp()
	
	rates = shikicore.user_rates(user_id=user_id, target_id=id)
	xbmc.log(str(rates))

	def line(n):
		result = u'{0}: {1}'.format(n, score_statuses.get(str(n)))
		return result

	options = [ line(n) for n in range(0, 11) ]
	
	if rates:
		r = rates[0]
		score = r['score']
		if score > 0:
			options[int(score)] = u'[COLOR yellow][B] * ' + options[int(score)] + ' * [/B][/COLOR]'
	else:
		#options[0] = u'[COLOR yellow][B] * ' + options[0] + ' * [/B][/COLOR]'
		xbmcgui.Dialog().notification(u'Shikimory.org V2', u'Для того, чтобы оценить, нужно сперва добавить в список')
		return
	
	index = xbmcgui.Dialog().contextmenu(list=options)
	if index >= 0:
		if rates:
			shikicore.update_user_rate(r['id'], score=index)


def status_list(user_id, plugin):
	rates = shikicore.user_rates(user_id=user_id)
	
	rr = {}
	for r in rates:
		status = r['status']
		if status in rr:
			rr[status].append(r)
		else:
			rr[status] = [r]
	
	result = []
	for index in range(len(rate_statuses)):
		status = rate_statuses[index]
		name = status_names[index]
	
		if status in rr:
			Ids = [ str(r['target_id']) for r in rr[status] ]
	
			res = { 'label': u'{0} ({1})'.format(name, len(Ids)),  'url': plugin.get_url(action='rate_list', status=status, ids=','.join(Ids))}
			result.append(res)
	
	return result
