def make_sentence(letters):
	out=''
	adjacency={}
	for i in range(len(letters)):
		(pos1,let1)=letters[i]
		print pos1
		for j in range(len(letters)):
			(pos2,let2)=letters[j]
			if is_adjacent(pos1,pos2):
				adjacency[(i,j)]='adjacent'
			elif is_space(pos1,pos2):
				adjacency[(i,j)]='space'


	for ((i,j),adj) in adjacency.iteritems():
		if adj=='adjacent':
			print letters[i][1]+letters[j][1]
		elif adj=='space':
			print letters[i][1]+' '+letters[j][1]
	return out

def is_adjacent(pos1,pos2):
	return abs(pos1[0]-pos2[0])<80 and abs(pos1[1]-pos2[0])<30

def is_space(pos1,pos2):
	return abs(pos1[0]-pos2[0])<200 and abs(pos1[1]-pos2[0])<30
