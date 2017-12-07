'''
Xander Beberman
Code Making, Code Breaking Final Project
cryptocomposer
'''

import numpy as np
import re
import string
import sys
import getopt
from subprocess import call
from dictionaries import Intervals, Notes
from dictionaries import LILYPOND_HEADER, LILYPOND_FOOTER, LILYPOND_MIDDLE

np.random.seed()

'''
Constants
'''
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]
PENTATONIC_SCALE = [0, 2, 3, 7, 9]

SCALE = MAJOR_SCALE
NOTE_LENGTH = "random"

'''
Penalty weights
'''
WEIGHT_IN_KEY = 3
WEIGHT_DIST_FROM_CENTER = 1
WEIGHT_SEQ_LENGTH = 2
WEIGHT_VOICE_LEADING = 1

class Note:
	'''
	Class used for note operations
	Begin by assuming everything is in C major and starts with center 0
	Notes are represented by their half-step distance from the center
	'''
	def __init__(self, value):
		'''
		degree is the scale degree of the note, in half-steps from the root
		'''
		self.value = value
		self.degree = value % 12

	def in_key(self):
		'''
		returns true if a note is in the major scale
		'''
		return (self.degree in SCALE)

'''
SEQUENCE FUNCTIONS
A sequence is a list of Notes
'''

def compute_sequence(seq):
	'''
	computes the shift of a sequence
	seq is a sequence of Notes
	'''
	product = 1
	addition = 0
	for i in range(1,len(seq)):
		if seq[i].value == seq[i-1].value:
			addition += 1
		else:
			product *= abs(seq[i].value - seq[i-1].value)
	return (product + addition) % 26

def check_sequence(seq, target):
	'''
	validates that the given sequence corresponds to the given shift
	seq is a sequence of Notes
	target is an int of the shift
	'''
	return (compute_sequence(seq) == (target % 26))

def calculate_penalties(seq, prev):
	'''
	calculates the penalties on a sequence
	seq is a sequence of Notes
	prev is a Note describing the last note in the previous sequence
	'''
	# print seq

	penalty_seq_length = max(len(seq) - 2, 0)
	penalty_voice_leading = abs(seq[0].value - prev.value)

	seq_in_key = [not n.in_key() for n in seq]
	# print seq_in_key
	penalty_in_key = sum(seq_in_key)

	seq_value_sqr = [(n.value**2) for n in seq]
	penalty_dist_from_center = sum(seq_value_sqr) / 25

	penalty = WEIGHT_IN_KEY*penalty_in_key + \
		WEIGHT_DIST_FROM_CENTER*penalty_dist_from_center + \
		WEIGHT_SEQ_LENGTH*penalty_seq_length + \
		WEIGHT_VOICE_LEADING*penalty_voice_leading
	return penalty

def make_sequence(start, intervals, choice="random"):
	'''
	generates a sequence of Notes from
	a given starting note and list of intervals
	start is a starting Note
	intervals is a list of intervals
	'''
	np.random.shuffle(intervals)
	seq = [start]
	for i in intervals:
		'''
		choosing whether interval goes up or down
		'''
		if (choice == "random"):
			coeff = np.random.choice([-1, 1])
		elif (choice == "up" or choice == 1):
			coeff = 1
		elif (choice == "down" or choice == -1):
			coeff = -1
		elif (choice == "center"):
			coeff = -1*np.sign(start.value)
		else:
			print "Error in make_sequence: choice given as " + str(choice)
			sys.exit(1)
		new = Note(seq[-1].value + coeff*i)
		seq.append(new)
	return seq

def add_doubles(seq, num):
	'''
	adds repeated notes to a sequence to add num to its product
	seq is a list of Notes
	num is an int of the number of repeated notes to add
	'''
	for i in range(0,num):
		j = np.random.randint(len(seq))
		seq.insert(j, seq[j])
	return seq

def make_possible_sequences(prev, target):
	'''
	prev is a Note describing the last note in the previous sequence
	target is the integer value of the shift to encode
	'''
	possible_sequences = []
	for i in Intervals[target]:
		for j in range(prev.value - 7, prev.value + 7):
			possible_sequences.append(make_sequence(Note(j), i))
	for i in Intervals[(target - 1) % 26]:
		for j in range(prev.value - 7, prev.value + 7):
			possible_sequences.append(add_doubles(make_sequence(Note(j), i), 1))
	return possible_sequences

def choose_sequence(prev, seqs):
	'''
	chooses the sequence with the smallest penalty
	prev is a Note describing the last note in the previous sequence
	seqs is a list of candidate sequences
	'''
	penalties = map(
		(lambda s: calculate_penalties(s, prev)),
		seqs)
	i = np.argmin(penalties)
	return seqs[i]

def shifts_to_sequences(shifts):
	'''
	makes and chooses sequences given a list of shifts
	shifts is a list of shifts
	'''
	prev = Note(0)
	seqs = []
	for s in shifts:
		candidates = make_possible_sequences(prev, s)
		seqs.append(choose_sequence(prev, candidates))
		prev = (seqs[-1])[-1]
	return seqs

def sequences_to_lilypond(seqs):
	'''
	converts a list of sequences to LilyPond notation
	'''
	notes = []
	for s in seqs:
		'''
		for each sequence, get note length
		'''
		if NOTE_LENGTH == "random":
			length = np.random.choice(['4','8','16'])
		else:
			length = NOTE_LENGTH
		for n in s:
			'''
			for each note in the sequence, get its octave and scale degree
			then add those to the output list
			'''
			note = Notes[n.degree]
			octave = n.value/12 + 1
			if (octave < 0):
				mark = ','
			else:
				mark = '\''
			for i in range(0,octave):
				note += mark
			note += length
			notes.append(note)
		if NOTE_LENGTH == "random":
			'''
			this part makes sure every sequence is quarter-note aligned
			'''
			length_int = int(length)
			length_seq = float(len(s)*4)/length_int
			length_rest = int(length_seq + 1) - length_seq
			length_rest = int(float(length_rest)/4*length_int)
			length_rest *= 16/length_int
			for l in [4, 2, 1]:
				for i in range(0,length_rest/l):
					notes.append('r' + str(16/l))
				length_rest = length_rest % l
		else:
			notes.append('r' + length)
	return ' '.join(notes)



'''
TEXT FUNCTIONS
'''

def clean_text(text):
	'''
	removes all punctuation and spacing from text and converts to uppercase
	text is a string to convert
	'''
	text = re.sub('[^a-zA-Z]+', '', text)
	text = text.upper()
	return text

def char_to_num(char):
	'''
	inputs an uppercase ascii character and returns its alphabet position
	char is an upperchase ascii character
	'''
	return(ord(char) - ord('A'))

def make_shifts(text):
	'''
	returns the shifts required to encrypt the text
	'''
	current = 0
	shifts = []
	for c in text:
		n = char_to_num(c)
		shifts.append((n - current) % 26)
		current = n
	return shifts


'''
FINAL FUNCTIONS
'''
def encrypt(text):
	text = clean_text(text)
	# print text
	shifts = make_shifts(text)
	# print shifts
	seqs = shifts_to_sequences(shifts)
	# print [[s.value for s in x] for x in seqs]
	lily = sequences_to_lilypond(seqs)
	return(lily)

def make_lilypond(lily, path_output, plaintext):
	'''
	creates three files: lilypond file (.ly), pdf of score, and MIDI filie
	lily is the note sequence to encode
	name is the path to the file without extension
	plaintext is the encrypted plaintext, to be used as the title of the piece
	'''
	path_ly = path_output+".ly"
	file_ly = open(path_ly, 'w')
	file_ly.write(LILYPOND_HEADER)
	file_ly.write(plaintext)
	file_ly.write(LILYPOND_MIDDLE)
	file_ly.write(lily)
	file_ly.write(LILYPOND_FOOTER)
	file_ly.close()

	call(["lilypond", "-o", path_output, path_ly])

def usage():
	print "USAGE: python cryptocomposer.py (-t TEXT | -i INPUT) (-o OUTPUT) [-s SCALE] [-l LENGTH] [-h]"
	print "\n\tINPUT\tplaintext to encode. -t takes precedence over -i"
	print "\n\tINPUT\t.txt file with plaintext to encode"
	print "\n\tOUTPUT\t.txt to which ciphertext is written"
	print "\n\tSCALE\tscale to use for in key penalties. Options are:"
	print "\t\tmajor\t\t(default) major scale"
	print "\t\tminor\t\tminor scale"
	print "\t\tharmnonic\tharmonic minor scale"
	print "\t\tpentatonic\tmajor pentatonic scale"
	print "\n\tLENGTH\tnote length to use when generating sequences. Options are:"
	print "\t\trandom\t\t(default) uses a random note length for every sequence"
	print "\t\t4, 8, 16\tuses standard quarter, eighth, or 16th notes"
	print "\n\t-h\tshow this screen"
	sys.exit(0)

def process_input(opts, args):
	if len(opts) < 2:
		usage()

	valid_lengths = ['4','8','16',"random"]
	plaintext = ""
	path_input = ""
	path_output = ""

	for opt, arg in opts:
		if opt == "-i":
			path_input = arg
		elif opt == "-o":
			path_output = arg
		elif opt == "-t":
			plaintext = arg
		elif opt == "-s":
			global SCALE
			if arg == "major":
				SCALE = MAJOR_SCALE
			elif arg == "minor":
				SCALE = MINOR_SCALE
			elif arg == "harmonic":
				SCALE = HARMONIC_MINOR_SCALE	
			elif arg == "pentatonic":
				SCALE = PENTATONIC_SCALE
			else:
				usage()
		elif opt == "-l":
			if str(arg) in valid_lengths:
				global NOTE_LENGTH
				NOTE_LENGTH = str(arg)
			else:
				usage()
		else:
			usage()

	if plaintext == "":
		if path_input == "":
			usage()
		else:
			file_in = open(path_input, 'r')
			plaintext = file_in.read()
			file_in.close()
	if path_output == "":
		usage()

	return plaintext, path_output


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 't:i:o:s:l:h')
		# print opts, args
	except getopt.GetoptError:
		usage()

	plaintext, path_output = process_input(opts, args)
	# print SCALE
	lily = encrypt(plaintext)
	make_lilypond(lily, path_output, plaintext)