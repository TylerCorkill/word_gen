
# Exception classes

class Duplicate(Exception):
	def __init__(self, value=True):
		self.value = value

# -------------------------------------

# Dictionary class

class Dictionary(object):
	def __init__(self):
		from json import loads
		from re import sub

		with open('.dict', "rb") as dictFile:
			self.dict = self.expand(dictFile)
		with open('.anti', 'rb') as anti:
			self.anti = self.expand(anti)

		# print self.dict
		# print self.anti

		# self.count = 0
		self.word = []
		self.dictlist = []
		self.antilist = []
		self.scan(self.dict)
		self.scan(self.anti, True)
		
		dictionary = ', '.join(self.dictlist)
		print 'Dictionary:', dictionary
		print 'Words:', len(self.dictlist)
		print 'Characters: %s\n' % len(sub('[, ]','',dictionary))

		antiDict = ', '.join(self.antilist)
		print 'Anti-Dictionary:', antiDict
		print 'Words:', len(self.antilist)
		print 'Characters: %s\n' % len(sub('[, ]','',antiDict))

	def scan(self, charDict, anti=False):	
		for char in charDict:
			if char != '*':
				self.word.append(char)
				# print charDict[char], char
				if '*' in charDict[char] or not charDict[char]:
					word = ''.join(self.word)
					try:
						if anti:
							self.antilist.append(word)
							if word in self.dictlist:
								raise Duplicate(word)
						else:
							self.dictlist.append(word)
							if word in self.antilist:
								raise Duplicate(word)
					except Duplicate as e:
						print 'Error> duplicate,' + e.value
				if charDict[char]:
					if anti:
						self.scan(charDict[char], True)
					else:
						self.scan(charDict[char])
				del self.word[-1]

	def shrink(self, dictIn):
		from json import dumps

		dictionary = dumps(dictIn)
		dictionary = dictionary.replace("\": {}, \"", "-")
		dictionary = dictionary.replace("\": {\"", "~")
		dictionary = dictionary.replace("*\": 0, \"", "*")
		dictionary = dictionary.replace("\": {}}, \"", "+")
		# print dictionary
		return dictionary

	def expand(self, dictIn):
		from json import loads

		dictionary = dictIn.read()
		dictionary = dictionary.replace("+", "\": {}}, \"")
		dictionary = dictionary.replace("*", "*\": 0, \"")
		dictionary = dictionary.replace("~", "\": {\"")
		dictionary = dictionary.replace("-", "\": {}, \"")
		# print dictionary
		dictionary = loads(dictionary)
		# print dictionary
		return dictionary

# ----------------------------------------------------------------------------

# Word class

class Word(Dictionary):

	def gen(self, maxLen, length=1):
		from json import loads

		alphabet = ['e','t','a','o','i','n','s',
					'h','r','d','l','c','u','m',
					'w','f','g','y','p','b','v',
					'k','j','x','q','z']
		# alphabet = ['m','w','f','g','y','p','b',
		# 			'v','k','j','x','q','z']
		# diction, antidict = False, False
		for char in alphabet:
			self.word.append(char)
			check = self.check()
			dictlist, antilist = 0, 0
			if check:
				word = ''.join(self.word)
				if check == 1:
					print '+', word
					self.dictlist.append(word)
					self.add(self.dict)
					if not dictlist: dictlist += 1
				elif check == 2:
					print '-', word
					self.antilist.append(word)
					self.add(self.anti)
					if not antilist: antilist += 1
			if length < maxLen:
				self.gen(maxLen, length + 1)
			del self.word[-1]
			self.commit(dictlist, antilist)

	def check(self):
		from urllib import urlopen
		from json import loads

		word = ''.join(self.word)
		if (word not in self.dictlist) and (word not in self.antilist):
			url = "http://api.urbandictionary.com/v0/define?term=" + word
			while True:
				try:
					if loads(urlopen(url).readline())["result_type"] == "exact":
						return 1
					else:
						return 2
				except:
					pass
		# else:
		# 	print '*', word
		return

	def add(self, charDict, pos=0):
		letter = self.word[pos]
		pos += 1
		if letter not in charDict:
			charDict[letter] = {}
		if pos < len(self.word):
			if len(charDict[letter]) != 0:
				charDict[letter]['*'] = 0
			self.add(charDict[letter], pos)

	def commit(self, dictlist, antilist):
		# self.count += 1
		# print self.count

		if dictlist:
			with open('.dict', 'wb') as f:
				f.truncate()
				f.write(self.shrink(self.dict))
		if antilist:
			with open('.anti', 'wb') as f:
				f.truncate()
				f.write(self.shrink(self.anti))

# ----------------------------------------------------------------------------


if __name__ == '__main__':
	start = Word()
	while True:
		try:
			start.length = int(raw_input('Length: '))
		except TypeError:
			print 'Number only'
		else:
			break
	start.gen(start.length)
	# Dictionary()