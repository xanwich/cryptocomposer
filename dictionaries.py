'''
List of intervals for choosing sequences
'''

Intervals = {
	0:	[[], [13, 2]],
	1:	[[1], [3,3,3]],
	2:	[[2], [2,2,7]],
	3:	[[3]],
	4:	[[2,2], [4], [2,3,5]],
	5:	[[5]],
	6:	[[2,3], [6], [2,2,2,2,2]],
	7:	[[7], [3,11]],
	8:	[[2,2,2], [2,4], [8], [2,17]],
	9:	[[3,3], [9], [5,7]],
	10:	[[2,5], [10], [2,2,3,3]],
	11:	[[11]],
	12:	[[2,2,3], [4,3], [2,6], [2,19]],
	13:	[[13], [3,13]],
	14:	[[2,7], [2,2,2,5]],
	15:	[[3,5]],
	16:	[[2,2,2,2], [2,8], [4,4], [2,3,7]],
	17:	[[17]],
	18:	[[2,3,3], [3,6], [2,9], [2,2,11]],
	19:	[[19], [3,3,9]],
	20:	[[2,2,5], [4,5], [2,10]],
	21:	[[3,7]],
	22:	[[2,11], [2,2,2,2,3]],
	23:	[[7,7]],
	24:	[[2,2,2,3], [2,4,3], [2,2,6], [4,6], [3,8], [2,5,5]],
	25:	[[5,5]]
}

# Octaves = {
# 	0:	'',
# 	1:	'\'',
# 	2:	'\'\'',
# 	3:	'\'\'\'',
# 	-1:	','.
# 	-2:	',,'.
# 	-3:	',,,'
# }

Notes = {
	0:	'c',
	1:	'des',
	2:	'd',
	3:	'ees',
	4:	'e',
	5:	'f',
	6:	'ges',
	7:	'g',
	8:	'aes',
	9:	'a',
	10:	'bes',
	11:	'b'
}

LILYPOND_HEADER = "\\version \"2.18.2\"\n\\header {\n  title = \""
LILYPOND_MIDDLE = "\"\n  composer = \"Cryptocomposer by Xander Beberman\"\n}\n\nmelody = {\n  \\clef treble\n  \\key c \\major\n  \\time 4/4\n  "
LILYPOND_FOOTER = "\n}\n\n\\score {\n  \\new Staff \\melody\n  \\layout { }\n  \\midi { }\n}"