
from scipy.stats import scoreatpercentile
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os

CORPUS_DIR = '/copyCats/pan-plagiarism-corpus-2009/intrinsic-detection-corpus/suspicious-documents/'

class Document:

	def __init__(self, name, doc_length, plag_passage_lengths):
		self.name = name
		self.doc_length = doc_length
		self.plag_passage_lengths = plag_passage_lengths
		self.num_plag_passages = len(plag_passage_lengths)
		if len(plag_passage_lengths) > 0:
			self.prop_of_plag_text = float(sum(plag_passage_lengths)) / len(plag_passage_lengths)
		else:
			self.prop_of_plag_text = 0.0

	def __str__(self):
		return '%s\t\t %i\t\t %i\t\t %f' % (self.name, self.num_plag_passages, self.doc_length, self.prop_of_plag_text)


def summarize_data():
	for directory in os.listdir(CORPUS_DIR):
		all_docs = explore_dir(directory)
		summarize_docs(directory, all_docs)
		print '---\n'*4

def summarize_docs(dirname, docs):
	print 'In directory', dirname
	num_plag = sum([d.num_plag_passages > 0 for d in docs])
	print float(num_plag) / len(docs), 'of the documents had some plagiarism'

	print 'The document lengths had the following distribution'
	five_num_summary([d.doc_length for d in docs])

	all_plag_lengths = []
	for d in docs:
		all_plag_lengths.extend(d.plag_passage_lengths)

	print 'The lengths of the instances of plag. had the following distribution'
	five_num_summary(all_plag_lengths)


def explore_dir(dir_name):
	# Parse out base names of all files in <dir_name>
	full_dir_path = CORPUS_DIR + dir_name + '/'
	
	all_file_bases = get_base_file_names(full_dir_path)
	feature_types = set()
	all_docs = []

	for file_base in all_file_bases:
		xml_full_path = full_dir_path + file_base + '.xml'
		text_full_path = full_dir_path + file_base + '.txt'

		doc_length = len(file(text_full_path, 'r').read())

		tree = ET.parse(xml_full_path)

		plag_lengths = []

		for feature in tree.iter('feature'):
			feature_types.add(feature.get('name'))
			
			if feature.get('name') == 'artificial-plagiarism':
				length = int(feature.get('this_length'))
				plag_lengths.append(length)
				
		doc = Document(file_base, doc_length, plag_lengths)
		all_docs.append(doc)


	return all_docs

def get_base_file_names(full_dir_path):
	all_files = os.listdir(full_dir_path)
	all_file_bases = [f[:-4] for f in all_files if f[-4:] == '.xml']

	return all_file_bases


def five_num_summary(arr):
	'''
	Prints <min, 25th percentile, median, 75th percentile, max>
	of data stored in <arr>
	'''
	min_val = min(arr)
	first_quart = scoreatpercentile(arr, 25)
	median = scoreatpercentile(arr, 50)
	third_quart = scoreatpercentile(arr, 75)
	max_val = max(arr)

	print min_val, first_quart, median, third_quart, max_val
	print 'Mean', sum(arr) / float(len(arr)), '\n'

if __name__ == '__main__':
	summarize_data() 