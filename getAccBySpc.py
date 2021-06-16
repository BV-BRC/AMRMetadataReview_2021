'''
python getAccBySpc.py [model_directory] [genome_lineage] <isMIC=False>
'''

from sys import argv,stderr
from glob import glob
import numpy as np
import scipy.stats
from sklearn.metrics import f1_score

# computes the 95% confidence interval
# taken from
#   https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
def mean_confidence_interval(data, confidence=0.95):
	a = 1.0 * np.array(data)
	n = len(a)
	m, se = np.mean(a), scipy.stats.sem(a)
	h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
	return [m, m-h, m+h]

# check if model_directory has with a '/'
# if not, add one
if argv[1][-1] != '/':
	argv[1] += 1

# check to see if we are computing stats for a MIC model
isMIC = False
if len(argv) > 3:
	if argv[3][0].lower() == 't':
		isMIC = True

# parse the header of the genome_lineage file
def parseHeader(f):
	headHsh = {}
	line = f.readline().strip('\n').split('\t')
	for i in range(0,len(line)):
		headHsh[line[i]] = i

	return headHsh

# parse the genome_lineage model
# outputs a hash that maps genome ID to species
def getSpcHsh():
	f = open(argv[2])

	# parse the header
	headHsh = parseHeader(f)
	# species hash to return
	spcHsh = {}
	# for each line
	#   get the species and genome ID
	#   add it to the hash
	for i in f:
		i = i.strip('\n').split('\t')
		# some species are longer than two "words"
		# clear out remaining "words"
		spc = ' '.join(i[headHsh['species']].strip().split(
					)[:2])
		gid = i[0]

		# if not species, continue
		if spc == '':
			continue

		spcHsh[gid] = spc

	f.close()

	return spcHsh

# parse a true file
# parameters are
#   true file name
#   species hash [getSPcHsh()]
# true file contains true order of the labels
#   genome ID
#   antibiotic
#   label
# returns table of true file
def parseTrue(tFile, spcHsh):
	f = open(tFile)

	# table to return
	trues = []
	# for each line
	#   split the line by tab
	#   split out the antibiotic
	#   convert the label to float
	#   append to table
	for i in f:
		i = i.strip().split('\t')
		ab = i[1].split(':')[0]
		spc = spcHsh[i[0]]
		val = round(float(i[-1]),0)

		trues.append([spc, ab, val])

	f.close()

	return trues

# parses prediction file
# parameters are
#   true table [parseTrue()]
#   prediction file name
# prediction file contains just predictions
# predictions correspond by line to the true file
def parsePred(trues, pFile):
	f = open(pFile)

	cnt = 0
	# for each line
	# append line contents to corresponding line number
	for i in f:
		val = round(float(i.strip()),0)
		trues[cnt].append(val)
		cnt += 1

	f.close()

# computes VME score
# parameters
#   array of true values
#   array of pred values
# return VME score
def vme_score(true, pred):
	vme = 0.0
	res = 0.0
	# for each element in true
	# if very major error, increment counter
	for i in range(0,len(true)):
		if true[i] == 2.0:
			res += 1.0
			if pred[i] == 0.0:
				vme += 1.0

	# if no resistance, return 0
	# otherwise, compute VME
	if res == 0:
		return 0
	else:
		return vme/res

# computes ME score
# parameters
#   array of true values
#   array of pred values
# return ME score
def me_score(true, pred):
	me = 0.0
	su = 0.0
	# for each element in true
	# if major error, increment counter
	for i in range(0,len(true)):
		if true[i] == 0.0:
			su += 1
			if pred[i] == 2.0:
				me += 1

	# if no susceptible, return 0
	# otherwise, compute ME
	if su == 0:
		return 0
	else:
		return me/su

# computes within 1 2-fold dilution factor score
# parameters
#   array of true values
#   array of pred values
# return within 1 2-fold dilution score
def w1_score(true, pred):
	w1 = 0.0
	# for each element in true
	# if within 1 two-fold dilution factor, increment counter
	for i in range(0,len(true)):
		if abs(true[i]-pred[i]) <= 1:
			w1 += 1.0

	# compute within 1 two-fold dilution score
	return w1/len(true)

# parses a single fold
# parameters
#   true file
#   pred file
#   species hash [getSpcHsh()]
# returns statistic hash for fold
def parseFold(tFile, pFile, spcHsh):
	# parse true and pred files
	trues = parseTrue(tFile, spcHsh)
	parsePred(trues, pFile)

	# initialize raw hash
	# rawHsh[species][antibiotic] = [[true],[pred]]
	rawHsh = {'ALL':{'ALL':[[],[]]}}
	# for each element in trues
	# split into spc, antibiotic, true val, pred val
	# initialize hash if not initialized
	# append to hash
	for i in trues:
		spc, ab, t, p = i
		if spc not in rawHsh:
			rawHsh[spc] = {'ALL':[[],[]]}
		if ab not in rawHsh[spc]:
			rawHsh[spc][ab] = [[],[]]
		if ab not in rawHsh['ALL']:
			rawHsh['ALL'][ab] = [[],[]]

		rawHsh[spc][ab][0].append(t)
		rawHsh[spc][ab][1].append(p)
		rawHsh['ALL'][ab][0].append(t)
		rawHsh['ALL'][ab][1].append(p)
		rawHsh[spc]['ALL'][0].append(t)
		rawHsh[spc]['ALL'][1].append(p)
		rawHsh['ALL']['ALL'][0].append(t)
		rawHsh['ALL']['ALL'][1].append(p)

	# stat hash to return
	# statHsh[species][antibiotic] = [f1, vme, me]
	# statHsh[species][antibiotic] = [w1]
	statHsh = {}
	# for each species-antibiotic in raw hash
	# compute f1, VME, and ME for SIR models
	# compute W1 for MIC models
	for i in rawHsh:
		statHsh[i] = {}
		for j in rawHsh[i]:
			true = rawHsh[i][j][0]
			pred = rawHsh[i][j][1]
			if isMIC:
				w1 = w1_score(true, pred)
				statHsh[i][j] = [w1]
			else:
				f1 = f1_score(true, pred, average='macro')
				vme = vme_score(true, pred)
				me = me_score(true, pred)
				statHsh[i][j] = [f1, vme, me]

	return statHsh

# merges stat hashes
# parameters
#   hash to merge to
#   hash to merge from
def mrgStatHsh(to, fr):
	# for each element in from
	# merge into to by appending
	for i in fr:
		if i not in to:
			to[i] = {}
		for j in fr[i]:
			if j not in to[i]:
				to[i][j] = []
				for k in range(0,len(fr[i][j])):
					to[i][j].append([])
			for k in range(0,len(fr[i][j])):
				to[i][j][k].append(fr[i][j][k])

# parses the entire model
def parseModel():
	# get the species hash
	spcHsh = getSpcHsh()

	# get the set of true files
	trues = glob(argv[1] + 'all/*true')
	# initialize the full statistic hash
	statsHsh = {}
	# for each true file
	#   get prediction file counterpart
	#   compute a single stat hash
	#   merge the stat hashes
	for tFile in trues:
		pFile = tFile.replace('true', 'pred', 1)
		statHsh = parseFold(tFile, pFile, spcHsh)
		mrgStatHsh(statsHsh, statHsh)

	# for each species in the stat hash
	for i in statsHsh:
		# for each antibiotic in the species stat hash
		#   compute average and CI for each stat
		#   update stats hash
		for j in statsHsh[i]:
			cis = []
			for k in statsHsh[i][j]:
				ci = mean_confidence_interval(k)
				cis += ci
			statsHsh[i][j] = cis

	return statsHsh

# gets a hash of indexed antibiotics
# parameters
#   hash of statistics [parseModel()]
def getAllAb(statsHsh):
	# antibiotic hash
	ab = {}
	# for each species in stat hash
	for i in statsHsh:
		# for each antibiotic in species stat hash
		# if antibiotic not in ab
		#   add it
		for j in statsHsh[i]:
			if j not in ab:
				ab[j] = 0

	cnt = 0
	# for each antibiotic
	#   add index count
	for i in sorted(ab):
		ab[i] = cnt
		cnt += 1

	return ab

# convert stat hash to matrix
# parameters
#   statistics hash [parseModel()]
# returns matrix
def toMat(statsHsh):
	# get antibiotics
	ab = getAllAb(statsHsh)

	# initialize matrix and array line
	mat = []
	arr = []
	# for each antibiotic add it to the line
	for i in sorted(ab, key = lambda x: ab[x]):
		if isMIC:
			arr += [i] + ['']*2
		else:
			arr += [i] + ['']*8
	arr = [''] + arr
	# print the heading
	mat.append(arr)

	# add subheading
	if isMIC:
		arr = ['W1', 'CI_Low', 'CI_High']*len(ab)
	else:
		arr = ['F1', 'CI_Low', 'CI_High', 'VME', 'CI_Low', 'CI_High', 'ME', 'CI_Low', 'CI_High']*len(ab)
	arr = ['Species'] + arr
	# print subheading
	mat.append(arr)

	# for each species in statistics hash
	for i in sorted(statsHsh):
		# initialize line
		arr = []
		if isMIC:
			arr = [0] * (len(ab)*3)
		else:
			arr = [0] * (len(ab)*9)

		# for each antibiotic in species stat hash
		for j in statsHsh[i]:
			# get line index from antibiotic index
			ind = -1
			if isMIC:
				ind = ab[j]*3
			else:
				ind = ab[j]*9

			# populate stats
			for k in range(0,len(statsHsh[i][j])):
				arr[ind+k] = statsHsh[i][j][k]

		# convert each element in array to string
		for j in range(0,len(arr)):
			if type(arr[j]) == int:
				arr[j] = ''
			arr[j] = str(arr[j])
		# add species to line
		arr = [i] + arr
		# add line to matrix
		mat.append(arr)

	return mat

# converts statistics hash to tabular format
# parameters
#   statsHsh [parseModel()]
# returns tabular formatted stats
def toTab(statsHsh):
	# initialize tabular
	tab = []

	# get heading
	arr = []
	if isMIC:
		arr += ['Species', 'Antibiotic', 'W1', 'CI_Low', 'CI_High']
	else:
		arr += ['Species', 'Antibiotic', 'F1', 'CI_Low', 'CI_High', 'VME', 'CI_Low', 'CI_High', 'ME', 'CI_Low', 'CI_High']
	# print heading
	tab.append(arr)

	# for each species in statistics hash
	for i in sorted(statsHsh):
		# for each antibiotic in species statistic hash
		for j in sorted(statsHsh[i]):
			# get line
			arr = [i,j] + statsHsh[i][j]
			# convert line to string
			for k in range(0,len(arr)):
				arr[k] = str(arr[k])
			# add line to tabular
			tab.append(arr)

	return tab

# prints a file out
# parameters
#   matrix/tabular file
#   file output name
def printFile(lst, fName):
	f = open(fName, 'w')

	# for each line in the list, write it to file
	for i in lst:
		f.write('\t'.join(i) + '\n')

	f.close()

# main function
# compute stats
# convert to matrix and tab
# print out files
def main():
	statsHsh = parseModel()
	mat = toMat(statsHsh)
	tab = toTab(statsHsh)

	printFile(mat, argv[1] + 'model.stats.mat')
	printFile(tab, argv[1] + 'model.stats.tab')

# run main if main
if __name__ == '__main__':
	main()
