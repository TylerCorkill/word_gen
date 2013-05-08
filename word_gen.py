from threading import Thread
from json import dumps, loads
from re import sub
from string import lowercase, digits
from urllib import urlopen
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
			self.dict = expand(dictFile)
		with open('.anti', 'rb') as anti:
			self.anti = expand(anti)

		# print self.dict
		# print self.anti

		# self.count = 0
		self.word = []
		self.dictlist = []
		self.antilist = []
		self.scan(self.dict, False)
		self.scan(self.anti, True)
		
		dictionary = ', '.join(self.dictlist)
		print 'Dictionary:', dictionary
		print 'Words:', len(self.dictlist)
		print 'Characters: %s\n' % len(dictionary.replace(', ',''))

		antiDict = ', '.join(self.antilist)
		print 'Anti-Dictionary:', antiDict
		print 'Words:', len(self.antilist)
		print 'Characters: %s\n' % len(antiDict.replace(', ',''))

	def scan(self, charDict, anti):	
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
						print 'Error: duplicate,' + e.value
				if charDict[char]:
					nextScan = Thread(target=self.scan, args=(charDict[char], anti))
					nextScan.start()
					nextScan.join()
					del nextScan
				del self.word[-1]

# ----------------------------------------------------------------------------

# Word class

class Word(Dictionary):

	def gen(self, maxLen, length=1):
		dictlist, antilist = 0, 0
		for char in (c for c in list(lowercase+digits)):
			self.word.append(char)
			check = self.check()
			if check:
				word = ''.join(self.word)
				if check == 1:
					print '+', word
					self.dictlist.append(word)
					Thread(target=self.add, args=(self.dict, 0)).start()
					if not dictlist: dictlist += 1
				elif check == 2:
					print '-', word
					self.antilist.append(word)
					Thread(target=self.add, args=(self.anti, 0)).start()
					if not antilist: antilist += 1
			if length < maxLen:
				nextGen = Thread(target=self.gen, args=(maxLen, length + 1))
				nextGen.start()
				nextGen.join()
				del nextGen
			del self.word[-1]
		Thread(target=self.commit, args=(dictlist, antilist)).start()

	def check(self):
		word = ''.join(self.word)
		if (word not in self.dictlist) and (word not in self.antilist):
			url = "http://api.urbandictionary.com/v0/define?term=" + word
			while True:
				try:
					if loads(urlopen(url).readline())["result_type"] == "exact":
						return 1
					else:
						return 2
				except KeyboardInterrupt:
					raise KeyboardInterrupt
				except:
					print "."
					continue
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
				f.write(shrink(self.dict))
		if antilist:
			with open('.anti', 'wb') as f:
				f.truncate()
				f.write(shrink(self.anti))

# ----------------------------------------------------------------------------

# Helper functions

def shrink(dictIn):
	from json import dumps

	dictionary = dumps(dictIn)
	dictionary = dictionary.replace("\": {}, \"", "-")
	dictionary = dictionary.replace("\": {\"", "~")
	dictionary = dictionary.replace("*\": 0, \"", "*")
	dictionary = dictionary.replace("\": {}}, \"", "+")
	# print dictionary
	return dictionary

def expand(dictIn):
	from json import loads

	dictionary = dictIn.read()
	dictionary = dictionary.replace("+", "\": {}}, \"")
	dictionary = dictionary.replace("*", "*\": 0, \"")
	dictionary = dictionary.replace("~", "\": {\"")
	dictionary = dictionary.replace("-", "\": {}, \"")
	# print dictionary
	dictionary = loads(dictionary)
	return dictionary

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