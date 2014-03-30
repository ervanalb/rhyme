#!/usr/bin/python

import pygame
from pygame.locals import *
import pygame.camera

import urllib2
import StringIO

import blob
import colorsys
from PIL import Image
import ImageFilter

class Camera:
	def __init__(self,size=(640,480)):
		self.size=size
		pygame.init()
		self.display = pygame.display.set_mode(self.size, 0)

	def pygame_webcam_init(self):
		pygame.camera.init()
		self.cam=pygame.camera.Camera("/dev/video0",self.size)
		self.cam.start()

	def web_frame_init(self,url):
		self.url=url

	def get_frame(self):
		print "fetch..."
		s=urllib2.urlopen(self.url).read()
		im = Image.open(StringIO.StringIO(s))
		print "resize..."
		im = im.resize(self.size,Image.ANTIALIAS)
		im=im.filter(ImageFilter.BLUR)
		letter_array=im.load()

		letter_array=[[(float(letter_array[x,y][0])/255.,float(letter_array[x,y][1])/255.,float(letter_array[x,y][2])/255.) for y in range(im.size[1])] for x in range(im.size[0])]
		print "process..."
		return letter_array

	def get_frame_webcam(self):
		s=self.cam.get_image()
		pa=pygame.PixelArray(s)
		def conv(p):
			c=s.unmap_rgb(p)
			return (float(c[0])/255.,float(c[1])/255.,float(c[2])/255.)
		return [[conv(pix) for pix in col] for col in pa]

	def show_frame(self,pixels):
		w=len(pixels)
		h=len(pixels[0])
		s=pygame.Surface((w,h))
		p=pygame.PixelArray(s)
		for x in range(w):
			for y in range(h):
				pix=pixels[x][y]
				p[x,y]=s.map_rgb(pix[0]*255.,pix[1]*255.,pix[2]*255.)
		del p

		self.display.blit(s, (0,0))
		pygame.display.flip()

	def run(self):
		going = True
		while going:
			self.process()
			events = pygame.event.get()
			for e in events:
				if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
					#self.cam.stop()
					going = False

	def process(self):
		p=self.get_frame()
		hsv=blob.convert(p,lambda x:colorsys.rgb_to_hsv(*x))
		def thresh((h,s,v)):
			return abs(h-176./360.) < 30./360. and s > 50./100.# and v > 10./100.

		blobs=blob.find_all(hsv,thresh)
		for b in blobs:
			b.draw(p)
			sc=blob.score(b,self.letters[0])
			if sc>0.8:
				self.letters[0].draw(p,b.center)
		self.show_frame(p)

if __name__=='__main__':
	c=Camera()
	c.web_frame_init('http://10.0.0.16:8080/photoaf.jpg')
	im=Image.open('letter_imgs/test.png')
	w,h=im.size
	ratio=4
	im=im.resize((w*ratio,h*ratio))
	c.letters=[blob.Letter(im,'test')]
	c.run()

