def convert(img,function):
	return [[function(pix) for pix in col] for col in img]

def find_all(img,threshold_function):
	thresh=convert(img,threshold_function)

	w=len(img)
	h=len(img[0])

	blobs=[[None]*h for x in range(w)]

	n=0
	for x in range(w):
		for y in range(h):
			if thresh[x][y] and blobs[x][y] is None:
				to_search=[(x,y)]
				while len(to_search)>0:
					(sx,sy)=to_search.pop()
					if sx>=0 and sy>=0 and sx<w and sy<h and thresh[sx][sy] and blobs[sx][sy] is None:
						blobs[sx][sy]=n
						to_search.append((sx+1,sy))
						to_search.append((sx-1,sy))
						to_search.append((sx,sy+1))
						to_search.append((sx,sy-1))
				n+=1

	return blobs

def color(img,blobs):
	w=len(img)
	h=len(img[0])

	COLORTABLE=[
		(1,0,0),
		(0,1,0),
		(0,0,1),
		(1,1,0),
		(0,1,1),
		(1,0,1),
	]

	def combine(pix,blob):
		if blob is None:
			return pix
		return COLORTABLE[blob%len(COLORTABLE)]

	return [[combine(img[x][y],blobs[x][y]) for y in range(h)] for x in range(w)]
