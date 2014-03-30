import numpy
import math

def convert(img,function):
	return [[function(pix) for pix in col] for col in img]

def find_all(img,threshold_function):
	thresh=convert(img,threshold_function)

	w=len(img)
	h=len(img[0])

	blobs=[[None]*h for x in range(w)]

	n=0
	blob_extents=[]
	for x in range(w):
		for y in range(h):
			if thresh[x][y] and blobs[x][y] is None:
				to_search=[(x,y)]
				sminx=x
				smaxx=x
				sminy=y
				smaxy=y
				while len(to_search)>0:
					(sx,sy)=to_search.pop()
					if sx>=0 and sy>=0 and sx<w and sy<h and thresh[sx][sy] and blobs[sx][sy] is None:
						blobs[sx][sy]=n
						sminx=min(sminx,sx)
						smaxx=max(smaxx,sx)
						sminy=min(sminy,sy)
						smaxy=max(smaxy,sy)
						to_search.append((sx+1,sy))
						to_search.append((sx-1,sy))
						to_search.append((sx,sy+1))
						to_search.append((sx,sy-1))
				blob_extents.append((sminx,smaxx,sminy,smaxy))
				n+=1

	individual_blobs = []
	for b in range(n):
		width=blob_extents[b][1]-blob_extents[b][0]+1
		height=blob_extents[b][3]-blob_extents[b][2]+1
		individual_blobs.append([[False]*height for x in range(width)])

	for x in range(w):
		for y in range(h):
			if blobs[x][y] is not None:
				b=blobs[x][y]
				bx=x-blob_extents[b][0]
				by=y-blob_extents[b][2]
				individual_blobs[b][bx][by]=True

	return [Blob(individual_blobs[b],(float(blob_extents[b][0]+blob_extents[b][1])/2.,float(blob_extents[b][2]+blob_extents[b][3])/2.)) for b in range(n)]

class Blob:
	def __init__(self,blob_array,center):
		self.array=numpy.array(blob_array)
		self.w=self.array.shape[0]
		self.h=self.array.shape[1]
		self.center=center

	def draw(self,img,color=(1,0,0)):
		ix=int(self.center[0]-float(self.w)/2.)
		iy=int(self.center[1]-float(self.h)/2.)

		for x in range(self.w):
			for y in range(self.h):
				if self.array[x,y]:
					img[ix+x][iy+y]=color

class Letter:
	def __init__(self,im,symbol):
		letter_array=im.load()
		def test(pix):
			return list(pix)[0]==0

		letter_array=[[test(letter_array[x,y]) for y in range(im.size[1])] for x in range(im.size[0])]
		self.array=numpy.array(letter_array)
		self.w=self.array.shape[0]
		self.h=self.array.shape[1]
		self.symbol=symbol

	def draw(self,img,center,color=(0,1,0)):
		ix=int(center[0]-float(self.w)/2.)
		iy=int(center[1]-float(self.h)/2.)

		for x in range(self.w):
			for y in range(self.h):
				if self.array[x,y]:
					img[ix+x][iy+y]=color

#def fastscore(blob,letter):
#	return float(min(sum(sum(l_a)),sum(sum(b_a)))) / max(sum(sum(l_a)),sum(sum(b_a)))

def score(blob,letter):
	b_a=blob.array
	l_a=letter.array

	diff_x=float(letter.w-blob.w)
	diff_y=float(letter.h-blob.h)

	if diff_x < 0: # blob bigger than letter
		l_a=numpy.pad(l_a,((int(math.floor(-diff_x/2)),int(math.ceil(-diff_x/2))),(0,0)),'constant')
	else: # letter bigger than blob
		b_a=numpy.pad(b_a,((int(math.floor(diff_x/2)),int(math.ceil(diff_x/2))),(0,0)),'constant')

	if diff_y < 0: # blob bigger than letter
		l_a=numpy.pad(l_a,((0,0),(int(math.floor(-diff_y/2)),int(math.ceil(-diff_y/2)))),'constant')
	else: # letter bigger than blob
		b_a=numpy.pad(b_a,((0,0),(int(math.floor(diff_y/2)),int(math.ceil(diff_y/2)))),'constant')

	return float(sum(sum(l_a*b_a))) / max(sum(sum(l_a)),sum(sum(b_a)))


