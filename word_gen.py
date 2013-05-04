
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

		with open("dict.txt", "rb") as dictFile:
			self.dict = loads(dictFile.read())
		with open('.antidict', 'rb') as anti:
			self.anti = loads(anti.read())
		self.word = []
		self.list = []
		self.antilist = []
		self.scan(self.dict)
		self.scan(self.anti, True)
		
		dictionary = ', '.join(self.list)
		print 'Dictionary:', dictionary
		print 'Words:', len(self.list)
		print 'Characters: %s\n' % len(sub('[, ]','',dictionary))

		antiDict = ', '.join(self.antilist)
		print 'Anti-Dictionary:', antiDict
		print 'Words:', len(self.antilist)
		print 'Characters: %s\n' % len(sub('[, ]','',antiDict))

	def scan(self, charDict, anti=False):	
		for char in charDict:
			if char != '*':
				self.word.append(char)
				if '*' in charDict[char] or not charDict[char]:
					word = ''.join(self.word)
					try:
						if anti:
							self.antilist.append(word)
							if word in self.list:
								raise Duplicate(word)
						else:
							self.list.append(word)
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
		diction, antidict = False, False
		for char in alphabet:
			self.word.append(char)
			check = self.check()
			if check:
				word = ''.join(self.word)
				if check == 1:
					if not diction:
						diction = True
					print '+', word
					self.list.append(word)
					self.add(self.dict)
				elif check == 2:
					if not antidict:
						antidict = True
					print '-', word
					self.antilist.append(word)
					self.add(self.anti)
			if length < maxLen:
				self.gen(maxLen, length + 1)
			del self.word[-1]
		self.commit(diction, antidict)

	def check(self):
		from urllib import urlopen
		from json import loads

		word = ''.join(self.word)
		if (word not in self.list) and (word not in self.antilist):
			url = "http://api.urbandictionary.com/v0/define?term=" + word
			if loads(urlopen(url).readline())["result_type"] == "exact":
				return 1
			else:
				return 2
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

	def commit(self, diction=False, antidict=False):
		from json import dumps

		if antidict:
			with open('.antidict', 'wb') as f:
				f.truncate()
				f.write(dumps(self.anti))
		if diction:
			with open('dict.txt', 'wb') as f:
				f.truncate()
				f.write(dumps(self.dict))

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