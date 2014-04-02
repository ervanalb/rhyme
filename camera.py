#!/usr/bin/python

import pygame
from pygame.locals import *
import pygame.camera

import urllib2
import StringIO

import blob
import sentence_maker

import colorsys
from PIL import Image
import ImageFilter

import json

class Camera:
	def __init__(self,size=(480,640)):
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

	def get_frame_fake(self):
		print "fetch..."
		im = Image.open('better_test.jpg')
		#im = im.rotate(-90)
		print "resize..."
		im = im.resize(self.size,Image.ANTIALIAS)
		#im=im.filter(ImageFilter.BLUR)
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

	def load_thresholds(self,filename):
		self.colors=json.load(open(filename))

	def load_letters(self,ratio):
		self.ratio=ratio
		alphabet="abcdefghijklmnopqrstuvwxyz"
		self.letters=[]
		for letter in alphabet:
			im=Image.open('letter_imgs/{0}.png'.format(letter))
			w,h=im.size
			im=im.resize((int(w*ratio),int(h*ratio)))
			self.letters.append(blob.Letter(im,letter))

	def load_freqs(self,filename):
		self.freqs=json.load(open(filename))

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
		#p=self.get_frame()
		p=self.get_frame_fake()
		hsv=blob.convert(p,lambda x:colorsys.rgb_to_hsv(*x))

		def get_thresh_func(color):
			hue=self.colors[color]['hue']
			sat=self.colors[color]['sat']
			val=self.colors[color]['val']
			hf=360
			sf=100
			vf=100
			if hue[0] < hue[1]:
				return lambda(h,s,v):h>=float(hue[0])/hf and h<=float(hue[1])/hf and s>=float(sat[0])/sf and s<=float(sat[1])/sf and v>=float(val[0])/vf and v<=float(val[1])/vf
			return lambda(h,s,v):(h>=float(hue[0])/hf or h<=float(hue[1])/hf) and s>=float(sat[0])/sf and s<=float(sat[1])/sf and v>=float(val[0])/vf and v<=float(val[1])/vf
			

		sentence=[]
		for color in self.colors:
			blobs=blob.find_all(hsv,get_thresh_func(color))
			for b in blobs:
				b.draw(p)
				plausible_letters = []
				for l in self.letters:
					sc=blob.score(b,l)
					if sc>0:
						plausible_letters.append((l,sc))
				if plausible_letters != []:
					l=max(plausible_letters,key=lambda x:x[1])
					l[0].draw(p,b.center)
					sentence.append(((float(b.center[0])/self.ratio,float(b.center[1])/self.ratio),l[0].symbol))
		self.show_frame(p)
		print sentence_maker.make_sentence(sentence)

if __name__=='__main__':
	c=Camera()
	c.load_thresholds('thresh')
	c.load_letters(0.36)
	#c.load_letters(0.4)
	c.web_frame_init('http://10.0.0.16:8080/photoaf.jpg')
	c.run()

