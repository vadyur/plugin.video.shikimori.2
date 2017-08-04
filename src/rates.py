# coding: utf-8

import shikicore
import xbmc, xbmcgui

rate_statuses = ('completed',	 'dropped',		 'on_hold',		 'planned',			 'rewatching',		 'watching')
status_names = (u'Просмотрено',	u'Брошено',		u'Отложено',	u'Запланировано',	u'Пересматриваю',	u'Смотрю')

def context_menu(id, user_id):

	options = [u'Ничего не выбрано'] + list(status_names)
	actions = ['nothing'] + list(rate_statuses)

	#import vsdbg; vsdbg._bp()
	
	rates = shikicore.user_rates(user_id=user_id, target_id=id)
	xbmc.log(str(rates))
	
	if rates:
		r = rates[0]
		i = actions.index(r['status'])
		if i > 0:
			options[i] = u'● ' + options[i]
	else:
		options[0] = u'● ' + options[0]
	
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
	
			res = { 'label': name,  'url': plugin.get_url(action='rate_list', status=status, ids=','.join(Ids))}
			result.append(res)
	
	return result
