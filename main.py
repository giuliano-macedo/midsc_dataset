import argparse
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import tqdm
from functools import reduce
def picksetfair(s):
	while True:
		ans=random.choice(s)
		if random.randrange(len(ans))==0:
			return ans
def genset(n):
	s=[set((i,)) for i in range(n)]
	for i in range(n//2):
		s1=picksetfair(s)
		s2=picksetfair(s)
		while s2==s1:
			s2=picksetfair(s)
		s1|=s2
		s.remove(s2)
	return s

def points_in_gaussian(pos,r,n):
	ans=[]
	for i in range(n):
		ans.append(np.array([(random.gauss(0,1)*(r/4))+p for p in pos]))
	return np.array(ans)
def random_point(min_x,max_x,min_y,max_y):
	return np.array([
		random.randrange(min_x,max_x),
		random.randrange(min_y,max_y),
		])
class Glob:
	def __init__(self,pos,vel,n,r):
		self.points=points_in_gaussian(pos,r,n)
		self.v=((np.random.rand(2)*2)-1)*vel
	def update(self):
		for p in self.points:
			p+=self.v
	def avg(self):
		n=len(self.points)
		ans0,ans1=0,0
		for point in self.points:
			ans0+=point[0]
			ans1+=point[0]
		return ans0/n,ans1/n

class Globs:
	def __init__(self,no_blobs,radius_blobs,no_points,limits,velocity):
		self.limits=[
			limits[0]+radius_blobs,
			limits[1]-radius_blobs,
			limits[2]+radius_blobs,
			limits[3]-radius_blobs
		]
		to_gen=[(random_point(*self.limits),s) for s in genset(no_blobs)]
		self.globs=[]
		for point,s in to_gen:
			for _ in s:
				self.globs.append(Glob(point,velocity,no_points//no_blobs,radius_blobs))
	def update(self):
		for glob in self.globs:
			x,y=glob.avg()
			# if (not self.limits[0]<=x<=self.limits[1]) or (not self.limits[2]<=y<=self.limits[3]):
			# 	glob.v*=-1.0
			glob.update()
	def get_points(self):
		ansx=[]
		ansy=[]
		for glob in self.globs:
			for point in glob.points:
				ansx.append(point[0])
				ansy.append(point[1])
		return ansx,ansy


def str2tuple4(s):
	ans=s.split(",")
	assert len(ans)==4
	return [float(a) for a in ans]

parser=argparse.ArgumentParser()
parser.add_argument("--no_points",type=int,default=500)
parser.add_argument("--radius_blobs",type=int,default=100)
parser.add_argument("--no_blobs",type=int,default=10)
parser.add_argument("--limits",type=str2tuple4,default="0,1000,0,1000")
parser.add_argument("--velocity",type=float,default=100)
parser.add_argument("--no_frames",type=int,default=10)
args=parser.parse_args()

globs=Globs(args.no_blobs,args.radius_blobs,args.no_points,args.limits,args.velocity)
ans=[]
reduce_concat=lambda X:reduce(lambda x,y:np.concatenate((x,y)),X)
for i in tqdm.tqdm(range(args.no_frames)):
	plt.axis(args.limits)
	ans.append(reduce_concat([point for point in (glob.points for glob in globs.globs)]))
	plt.scatter(*globs.get_points(),marker="o",s=1)
	plt.savefig(os.path.join("imgs",f"frame_{i+1:02}.png"))
	plt.clf()
	globs.update()
ans=reduce_concat(ans)
np.savetxt("results.csv", ans, delimiter=",")


os.system("rm wow.mp4")
os.system(r"ffmpeg -loglevel panic -framerate 1 -i imgs/frame_%02d.png wow.mp4")
# os.system("rm -f imgs/*")