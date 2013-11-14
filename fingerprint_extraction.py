# fingerprint_extraction.py
# Module for generating fingerprints from documents.

import nltk
import string, random, re
import itertools

# TODO: omit words tokenized by nltk that are just puncuation
# TODO: for anchor selection, get some empirical data about the frequency of permutations of 3-charactor strings are

class FingerprintExtractor:

	def __init__(self):
		self.hash_span = 1000
		self.anchors = ['ul', 'ay', 'oo', 'yo', 'si', 'ca', 'am', 'ie', 'mo', 'rt']
		pass

	def _gen_string_hash(self, in_string):
		'''
		Converts the given string <in_string> to an integer which is
		roughly uniformly distributed over all possible values.

		This method is used in "Methods for Identifying Versioned and 
		Plagiarized Documents".
		'''
		if len(in_string) == 0:
			return 0
		elif len(in_string) == 1:
			return ord(in_string)
		hash_list = [ord(in_string[0])] # TODO: what should the 0th element be?
		for i in xrange(1, len(in_string)):
			cur_char = in_string[i]
			res = hash_list[i-1]^(ord(cur_char) + (hash_list[i-1]<<6) + (hash_list[i-1]>>2))
			hash_list.append(res)
		return hash_list[-1] % self.hash_span

	def get_fingerprint(self, document, n, method="full", k=5):
		'''
		Returns a fingerprint, or list of minutiae, for the given document.

		There are several key pieces involved in fingerprinting:
		1: Converting n-grams to integers using a hash function
		2: Granularity, or size of the n-grams (more simply, the size of n)
		3: Resolution, or the number of minutiae used to represent the fingerprint
		4: Selection Strategy, which is the method used to select n-grams from the document
		'''
		if method == "full":
			words = nltk.tokenize.punkt.PunktWordTokenizer().tokenize(document)
			fingerprint = self._get_full_fingerprint(words, n)
		elif method == "kth_in_sent":
			sentences = nltk.tokenize.punkt.PunktSentenceTokenizer().tokenize(document)
			fingerprint = self._get_kth_in_sent_fingerprint(sentences, n, k)
		elif method == "anchor":
			fingerprint = self._get_anchor_fingerprint(document, n)

		return fingerprint
	
	def _get_full_fingerprint(self, words, n):
		fingerprint = []
		for i in xrange(len(words) - n + 1):
			fingerprint.append(self._gen_string_hash(" ".join(words[i:i+n])))
		return fingerprint

	def _get_kth_in_sent_fingerprint(self, sentences, n, k):
		fingerprint = []
		for sent in sentences:
			split_sent = sent.split()
			L = len(split_sent)
			# We want the n-gram beginning at word k, but if k > len(sentence) or n > len(sentence)
			# then we want the longest n-gram we can find (perhaps the whole sentence).
			fingerprint.append(self._gen_string_hash(" ".join(split_sent[min(k, L - min(n, L)) : min(k + n, L)])))
		return fingerprint

	def gen_anchors(anchor_length = 2, num_anchors=10):
		"""
		This function should be called whenever we want to generate a new list of
		anchors. Just set self.anchors equal to the result of this function.
		"""
		alphabet = string.ascii_lowercase
		# look at all permutations
		anchor_counts = {}
		for anchor in itertools.product(alphabet, repeat=anchor_length):
			anchor = "".join(anchor)
			anchor_counts[anchor] = 0
		print anchor_counts

		corp = nltk.corpus.gutenberg
		for filename in corp.fileids():
			print 'Counting anchors in', filename
			for anchor in anchor_counts.keys():
				results = re.findall(anchor, corp.raw(filename))
				anchor_counts[anchor] += len(results)

		# sort keys in decreasing order
		anchors = anchor_counts.keys()
		anchors = filter(lambda x: anchor_counts[x] != 0, sorted(anchors, key=lambda x: anchor_counts[x], reverse=True))
		for a in anchors:
			print a, anchor_counts[a]

		start_index = int(0.15*len(anchors))
		return anchors[start_index:start_index+num_anchors]
		

	def _get_anchor_fingerprint(self, document, n):
		# anchors are start or middle of n-gram?
		fingerprint = []
		for anchor in self.anchors:
			# Our regular expression puts the word containing the anchor in the middle of the n-gram
			# tie is resolved with an extra word at the end
			regex = '\w+\s+' * ((n - 1) / 2) + '\w*' + anchor + '\w*' + '\s+\w+' * ((n - (n%2) )/2)
			for match in re.finditer(regex, document):
				fingerprint.append(self._gen_string_hash(match.group(0)))
		return fingerprint


if __name__ == '__main__':
	ex = FingerprintExtractor()
	corp = nltk.corpus.gutenberg

	print ex.get_fingerprint(corp.raw("austen-sense.txt"), 3, "anchor")
	print ex.get_fingerprint(corp.raw("austen-emma.txt"), 3, "anchor")

