#!/usr/bin/env python3
# Name: Ioannis Anastopoulos
# Date: 11/20/2017

'''Program calculates transition and emission probabilities given a threshold theta, and a multiple alignment. '''

import sys
import numpy as np
from collections import defaultdict

class HMM():
	def __init__(self,theta,alphabet,alignment_length,grey_alignment_columns, clear_alignment_columns,m_alignment):
		''' theta is the given threshold
		    alphabet is the chars that are emitted by the hidden states
		    alignment_length is the length of the alignment
		    grey_alignment_columns ar ethe insert columns that are above theta
		    clear_alignment_columns are the match/delete columns that are below theta'''
		self.theta = theta
		self.alphabet = alphabet
		self.alignment_length = alignment_length
		self.grey_alignment_columns = grey_alignment_columns
		self.clear_alignment_columns=clear_alignment_columns
		self.m_alignment=m_alignment

	def transEmissionCounts(self):
		'''Method counts occurence of transition states, and emission chars'''
		transition_counts=defaultdict(dict)
		transition_counts['S']={} #initializing transition dict
		transition_counts['S']['M1']=0
		transition_counts['S']['D1']=0
		transition_counts['S']['I0']=0

		emission_counts=defaultdict(dict)

		for item in self.m_alignment: #iterating through each sequence in alignment
			item_states=[] #list of tuples(state, emission) of each sequence in alignment
			counter=0
			for i, char in enumerate(item):
				if i in self.clear_alignment_columns and char!="-":
					counter+=1 #increment each time you are in clear column
					item_states.append(('M'+str(counter), char))
				if i in self.clear_alignment_columns and char=="-":
					counter+=1#increment each time you are in clear column
					item_states.append(('D'+str(counter), char))
				if i in self.grey_alignment_columns and char!="-":
					item_states.append(('I'+str(counter), char)) #counter not incremented if i not in clear
			###------------Counting transition and emissions--------------###
			transition_counts['S'][item_states[0][0]]+=1

			if 'E' not in transition_counts[item_states[len(item_states)-1][0]]:
				transition_counts[item_states[len(item_states)-1][0]]['E']=0
			transition_counts[item_states[len(item_states)-1][0]]['E']+=1
			
			for i in range(len(item_states)-1):
				if item_states[i][0] in transition_counts and item_states[i+1][0] in transition_counts[item_states[i][0]]:
					transition_counts[item_states[i][0]][item_states[i+1][0]]+=1
				else:
					transition_counts[item_states[i][0]][item_states[i+1][0]]=1				
			for i in range(len(item_states)):
				if item_states[i][0] in emission_counts and item_states[i][1] in emission_counts[item_states[i][0]]:
					emission_counts[item_states[i][0]][item_states[i][1]]+=1
				else:
					emission_counts[item_states[i][0]][item_states[i][1]]=1
			###------------Counting transition and emissions--------------###
		return(transition_counts, emission_counts)
	
	def MatrixBuild(self, transition_counts, emission_counts):
		'''Method converts transition_counts and emission_counts from dict of dicts to numpy matrices
		   and normalizes them'''
		transition_alphabet = [] #possible states of the alignment
		for i in range(self.alignment_length-len(self.grey_alignment_columns)+1):
			for char in 'MD':
				if i!=0:
					transition_alphabet.append(char+str(i))
			transition_alphabet.append('I'+str(i))
		transition_alphabet.insert(0, 'S')
		transition_alphabet.append('E') #alphabet of all possible states the alignment can go through

		transitions_alphabet = {char:i for i,char in enumerate(transition_alphabet)} #state and its index in the transition alphabet to be used in building numpy matrix
		emissions_alphabet = {char:i for i,char in enumerate(self.alphabet)} #emission and its index in the transition alphabet to be used in building numpy matrix
		#initiating matrices of zeros
		transition_matrix = np.zeros(shape=(len(transition_alphabet), len(transition_alphabet)))
		emission_matrix = np.zeros(shape=(len(transition_alphabet), len(self.alphabet)))
		###--------------------Filling in both transition and emission matrices with their probabilities--------------------###
		for key in transition_counts:
			for subkey in transition_counts[key]:
				transition_matrix[transitions_alphabet[key],transitions_alphabet[subkey]]=np.float64(transition_counts[key][subkey])/sum(transition_counts[key].values())
		for key in emission_counts:
			for subkey in emission_counts[key]:
				if 'D' not in key:
					emission_matrix[transitions_alphabet[key],emissions_alphabet[subkey]]=np.float64(emission_counts[key][subkey])/sum(emission_counts[key].values())
		###--------------------Filling in both transition and emission matrices with their probabilities--------------------###
		return(transition_alphabet, transition_matrix, emission_matrix)
		
	def wrap(self):
		transition_counts, emission_counts =self.transEmissionCounts()
		return(self.MatrixBuild(transition_counts,emission_counts))


def file_parse():
	'''Function parses input file and returns threshold,emission alphabet,length of alignment,
	   list of column indexes of insert columns, list of column indexes of match/delete columns, and multiple alignment'''
	m_alignment = []
	grey_alignment_columns=[]
	clear_alignment_columns=[]

	with sys.stdin as fn:
		lines = fn.readlines()
		theta = float(lines[0])
		alphabet = lines[2].split()
		for line in lines[4:]:
			m_alignment.append(line.rstrip())
			alignment_length = len(line)#length of alignment SHOULD ADD EDGE CASE WHERE NOT ALL ITEMS IN LINES ARE THE SAME LENGTH
		space_occurence ={i:0 for i in range(alignment_length)} #creating dict of each position and count of spaces in each position

	for item in m_alignment:
		for i in range(len(item)):
			if item[i]=='-':
				space_occurence[i]+=1#counting spaces in each column

	for key in space_occurence:
		space_occurence[key] = space_occurence[key]/len(m_alignment)#occurence of space in each column
		if space_occurence[key] >= theta:
			grey_alignment_columns.append(key) #columns that exceed theta
		
	for item in list(range(alignment_length)):
		if item not in grey_alignment_columns:
			clear_alignment_columns.append(item)# columns that do not exceed theta

	return(theta,alphabet,alignment_length,grey_alignment_columns, clear_alignment_columns,m_alignment)


def main():
	theta,alphabet,alignment_length,grey_alignment_columns, clear_alignment_columns,m_alignment=file_parse()
	res=HMM(theta,alphabet,alignment_length,grey_alignment_columns, clear_alignment_columns,m_alignment)
	transition_alphabet, transition_matrix, emission_matrix= res.wrap()
	### -------------Printing matrix ------------ ####
	print('\t'+'\t'.join(char for char in transition_alphabet))
	for i,e in enumerate(transition_alphabet):
		for index in range(len(transition_matrix)):
			if index==i:
				print(e+'\t'+'\t'.join(format(num,".3f") for num in transition_matrix[index]))			
	print('--------')
	print('\t'+'\t'.join(char for char in res.alphabet))
	for i,e in enumerate(transition_alphabet):
		for index in range(len(transition_matrix)):
			if index==i:
				print(e+'\t'+'\t'.join(format(num,".3f") for num in emission_matrix[index]))

if __name__ == "__main__":
	main()