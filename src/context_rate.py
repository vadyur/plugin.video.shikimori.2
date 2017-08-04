# coding: utf-8

import sys

li = sys.listitem
it = li.getVideoInfoTag()

import shikicore
if shikicore.authorize_me():

	oo = shikicore.animes_search(it.getOriginalTitle())
	if oo:
		from rates import context_menu
		context_menu(oo[0]['id'], shikicore.whoami()['id'])
