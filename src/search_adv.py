# coding: utf-8

from simpleplugin import MemStorage

class SearchAdv(object):

	def __init__(self):
		''' '''
		self.storage = MemStorage('shiki.SearchAdv')

	# --------------------------------------------------------------------------------------
	years = property()

	@years.getter
	def years(self):
		return self.storage.get('years')

	@years.setter
	def years(self, value):
		self.storage['years'] = value

	@years.deleter
	def years(self):
		del self.storage['years']

	@staticmethod
	def years_list():
		import datetime
		now = datetime.datetime.now()

		return [ year for year in xrange(now.year, 1990, -1) ]

	# --------------------------------------------------------------------------------------
	genres = property()

	@genres.getter
	def genres(self):
		return self.storage.get('genres', [])

	@genres.setter
	def genres(self, value):
		self.storage['genres'] = value

	@genres.deleter
	def genres(self):
		del self.storage['genres']

	def genres_dict(self):
		import shikicore

		if 'genres_dict' not in self.storage:
			self.storage['genres_dict'] = [ genre for genre in shikicore.genres() if genre['kind'] == 'anime' ]
		return self.storage['genres_dict']

	@property
	def genre_ids(self):
		l = self.genres

		return [ genre['id'] for genre in SearchAdv().genres_dict() if genre['russian'] in l ]

	@staticmethod
	def genres_list():
		return sorted([ genre['russian'] for genre in SearchAdv().genres_dict() ])

	# --------------------------------------------------------------------------------------
	score = property()

	@score.getter
	def score(self):
		return self.storage.get('score')

	@score.setter
	def score(self, value):
		self.storage['score'] = value

	@score.deleter
	def score(self):
		del self.storage['score']

	@staticmethod
	def scores_list():
		#import shikicore
		from rates import score_statuses

		def line(n):
			result = u'{0}: {1}'.format(n, score_statuses.get(str(n)))
			return result

		return [ line(n) for n in range(1, 10) ]


	# --------------------------------------------------------------------------------------
	rating = property()

	@rating.getter
	def rating(self):
		return self.storage.get('rating', [])

	@rating.setter
	def rating(self, value):
		self.storage['rating'] = value

	@rating.deleter
	def rating(self):
		del self.storage['rating']

	@staticmethod
	def ratings_keys():
		return ['g', 'pg', 'pg_13', 'r', 'r_plus', 'rx']

	@staticmethod
	def ratings_dict():
		return {
			'g': u"G - Нет возрастных ограничений",
			'pg': u"PG - Рекомендуется присутствие родителей",
			'pg_13': u"PG-13 - Детям до 13 лет просмотр не желателен",
			'r': u"R - Лицам до 17 лет обязательно присутствие взрослого",
			'r_plus': u"R+ - Лицам до 17 лет просмотр запрещен",
			'rx': u"Rx - Хентай"
		}

	@staticmethod
	def ratings_list():
		rk = SearchAdv.ratings_keys()
		return [ SearchAdv.ratings_dict()[r] for r in rk ]

	