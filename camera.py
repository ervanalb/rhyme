#!/usr/bin/python

import pygame
import pygame.camera
from pygame.locals import *

import blob
import colorsys

class Camera:
	def __init__(self,size=(640,480)):
		self.size=size
		pygame.init()
		pygame.camera.init()
		self.cam=pygame.camera.Camera("/dev/video0",self.size)
		self.cam.start()
		self.display = pygame.display.set_mode(self.size, 0)

	def get_frame(self):
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
					self.cam.stop()
					going = False

	def process(self):
		p=self.get_frame()
		hsv=blob.convert(p,lambda x:colorsys.rgb_to_hsv(*x))
		blobs=blob.find_all(hsv,lambda x:x[2]>0.8)
		p=blob.color(p,blobs)
		self.show_frame(p)

if __name__=='__main__':
	c=Camera()
	c.run()