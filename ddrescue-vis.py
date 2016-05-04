#!/usr/bin/env python3
import math,svgwrite
#from svgwrite import cm, mm  



# Assume fun is a strictly monotonic function
def search(guess,fun,want,epsilon):
	# Many of our examples will have guess=left edge of domain, so
	# figure out if fun is increasing or decreasing by moving to the right
	guessVal=fun(guess)
	if fun(guess+(1/1000))<guessVal:
		# Decreasing.
		# Make our job easier by allowing us to assume the function is increasing
		return search(guess,lambda x:-fun(x),-want,epsilon)

	# This function searches positive numbers until some condition is reached,
	# verifying some comparison at each step
	def doublerFind(f,donewhen,verify):
		prevVal=f(0)
		t=1
		while True:
			tVal=f(t)
			if not(verify(prevVal,tVal)):
				raise Exception("condition not right")
			if donewhen(tVal):
				return t
			t=2*t
			prevVal=tVal

	# Need to search for the other boundary point
	#                  |  fun increasing 
	#  guess too small |   go right      
	#  guess too big   |   go left       
	get_bigger = lambda old,new:(old<new)
	get_smaller= lambda old,new:(old>new)

	if guessVal<want:
		lowT=guess
		g=lambda x:guess+x
		highT=g(doublerFind(lambda x:fun(g(x)),lambda y:y>want,get_bigger))
	elif guessVal>want:
		highT=guess
		g=lambda x:guess-x
		lowT=g(doublerFind(lambda x:fun(g(x)),lambda y:y<want,get_smaller))
	else:
		return guess

	#print("Searching [%f,%f] of fun for val %f" % (lowT,highT,want))

	# Now do a binary search
	#                     |  fun increasing 
	#  midpoint too small |   change low    
	#  midpoint too big   |   change high   
	while True:
		halfT=(lowT+highT)/2
		halfTVal=fun(halfT)
		#print("Searching [%f,%f] of fun for val %f; midpt has val=%f" % (lowT,highT,want,halfTVal))
		if math.fabs(halfTVal-want)<epsilon:
			break
		if halfTVal<want:
			lowT=halfT
		elif halfTVal>want:
			highT=halfT
		else:
			print('Should not happen')
	return halfT

def search_test():
	eps=1/1000
	want=5
	f=lambda x:x
	assert(math.fabs(f(search(1 ,f,want,eps))-want)<eps)
	assert(math.fabs(f(search(10,f,want,eps))-want)<eps)
	f=lambda x:-x
	want=-5
	assert(math.fabs(f(search(1 ,f,want,eps))-want)<eps)
	assert(math.fabs(f(search(10,f,want,eps))-want)<eps)


class ParamCurve:
	"""a parametrized 2D curve"""
	def pos(self,t):
		return (0,0)
	def speed(self,t):
		return 0
	def arclengthUpTo(self,t):
		return 0
	def radius(self,t):
		p=self.pos(t)
		return math.sqrt((p[0])**2+(p[1])**2)
	def findTWithGivenArclength(self,al,epsilon):
		return search(0,self.arclengthUpTo,al,epsilon)
	def findTWithGivenRadius(self,r,epsilon):
		return search(0,self.radius,r,epsilon)
	def getPoints(self,t0,t1,epsilon):
		# Get a list of points along the curve from t=t0..t1.
		# Try to ensure they are pairwise closer than epsilon
		if t0<t1:
			direction=+1
		elif t0>t1:
			direction=-1
		else:
			return [self.pos(t)]
	
		t=t0
		l=[]
		while ((direction==+1 and t<t1) or (direction==-1 and t>t1)):
			l.append(self.pos(t))
			tspeed=self.speed(t)
			#print("t=%f and speed=%f" % (t,tspeed))
			# Want to go a distance of <epsilon.  D=r*t, so
			t=t+direction*(epsilon/tspeed)
		l.append(self.pos(t1))
		print("Got %d points" % len(l))
		return l
	def getPointsN(self,t0,t1,N):
		# Get a list of N+1 points along the curve from t=t0..t1.
		l=[]
		delta=(t1-t0)/N
		for i in range(0,N):
			l.append(self.pos(t0+delta*i))
		l.append(self.pos(t1))
		print("Got %d points" % len(l))
		return l

	
class ArchimedeanSpiral(ParamCurve):
	# A CD rotates counterclockwise as seen from above the label.
	# From the bottom it looks like it's rotating clockwise, but that means
	# we're reading a track that goes counterclockwise.
	#   theta(t)=t, r(t)=k*t
	# so:
  #   x(t)=r(t)*cos(theta(t))=k*t*cos(t)
	#   y(t)=r(t)*sin(theta(t))=k*t*sin(t)
	# pitch = Distance between spirals=2*k*pi
	def __init__(self,pitch):
		self.k=pitch/(2*math.pi)
		#print("k=%f" % self.k)
	def pos(self,t):
		return (self.k*t*math.cos(t),self.k*t*math.sin(t))
	def speed(self,t):
		#print("speed for t=%f with k=%f" % (t,self.k))
		return self.k*math.sqrt(1+t**2)
	def arclengthUpTo(self,t):
		return self.k*((1/2)*t*(math.sqrt(1+t**2))+math.log(math.fabs(math.sqrt(1+t**2)+t)))



def curveToSVGPath(l,pathType="S"):
	# See http://svgdiscovery.com/E3/E3.htm
	# Given a list like: [(1,2),(3,4),(5,6),(7,8)], this should
	# return a string like "M1,2 S 3 4 5 6 7 8" which means:
	#  start at (1,2) and draw a smooth bezier curve through the points
	#  (3,4), (5,6), (7,8)

	# Otherwise we'll have SVG errors
	assert(len(l)>2)
	# certain pathtypes must have either an odd or even number of points
	if len(l) % 2==0:
		l.append(l[-1])
	P=l[0]
	outList=["M"+str(P[0])+" "+str(P[1])+" "+pathType]
	for i in range(1,len(l)):
		P=l[i]
		outList.append(str(P[0]))
		outList.append(str(P[1]))
	return ' '.join(outList)



MICRON_TO_MM=1.0e-3
NANOMETER_TO_MM=1.0e-6

class DiskGeometry:
	def __init__(self,radiusInner,radiusOuter,dataRadiusInner,dataRadiusOuter,byteLength,c):
		# In mm
		self.radiusInner=radiusInner
		self.radiusOuter=radiusOuter
		self.dataRadiusInner=dataRadiusInner
		self.dataRadiusOuter=dataRadiusOuter
		# This is the length of a byte, in mm, on the track, including error correction
		self.byteLength=byteLength

		self.curve=c
		self.tInner=c.findTWithGivenRadius(dataRadiusInner,NANOMETER_TO_MM/10)
	def byteToT(self,b):
		# the curve is not unit speed, so we need to use arc length
		# 0th byte should correspond to tInner
		return self.curve.findTWithGivenArclength(self.tInner+b*self.byteLength,NANOMETER_TO_MM/10)
	def TToByte(self,t):
		return (self.curve.arclengthUpTo(t)-self.curve.arclengthUpTo(self.tInner))/(self.byteLength)



# How bits translate to on-disk format:
# https://en.wikipedia.org/wiki/Compact_disc
# https://en.wikipedia.org/wiki/Eight-to-fourteen_modulation
# https://en.wikipedia.org/wiki/Cross-interleaved_Reed%E2%80%93Solomon_coding
#https://books.google.com/books?id=xCXVGneKwScC&lpg=PA383&ots=9lN26eWisY&dq=cd%20spiral%20(clockwise%20OR%20counterclockwise)&pg=PA389#v=onepage&q=cd%20spiral%20(clockwise%20OR%20counterclockwise)&f=false






# Good resource:
# https://commons.wikimedia.org/wiki/File:Comparison_CD_DVD_HDDVD_BD.svg

# Can have long pits to represent a series of identical bits, so sources
# say 'minimum pit length' (?)
# http://ecee.colorado.edu/~ecen5616/WebMaterial/DVD_Optical_System_Design.pdf
# single-sided: pit length in (0.40,1.87) micrometers
# double-sided: pit length in (0.44,2.13) micrometers
#
# even better:
# https://books.google.com/books?id=E1p2FDL7P5QC&lpg=PA717&ots=M3okDc3ZhB&dq=dvd%20length%20of%20byte&pg=PA717#v=onepage&q=dvd%20length%20of%20byte&f=false


#dvd_1side_1layer=DiskGeometry(
#	32/2,
#	120/2,
#	40/2,
#	117.5/2,
#	0.74*MICRON_TO_MM,
#	1.0, # TODO ecc
#	ArchimedeanSpiral(0.4*MICRON_TO_MM ))

# DVD5 is 1-side, 1-layer
dvd5=DiskGeometry(22,60,24,58.0,
	# on a DVD a sector has 2048 bytes.
	#  data frame = sector + various info = 2064 bytes
	#  ecc frame = data frame + ecc information = 2366 bytes
	# Then each group of 91 bytes in the ecc frame is converted to
	#  182 bytes + 4 bytes of synchronization data = 186
	# giving 4836 on-disk bytes per sector
	# But all we really need to know is that on-disk, a sector has a length of
	# 5.16 mm, supposedly.
	5.16/2048,
	ArchimedeanSpiral(0.74 * MICRON_TO_MM))
	#ArchimedeanSpiral(0.4 * MICRON_TO_MM))

def parse_logfile(logfile):
	# logfile is a log from ddrescue
	blocks_good=[]
	blocks_bad=[]
	blocks_unknown=[]
	block_current=-1
	# This will apparently automatically close the file?
	with open(logfile,'r') as f:
		for s in f:
			if s[0]=='#':
				continue;
			l=s.split()
			if block_current<1:
				block_current=int(l[0],base=0)
			else:
				switcher={"+": blocks_good, "-": blocks_bad, "/": blocks_unknown, "*": blocks_unknown}
				b=switcher.get(l[2],"nothing")
				if b=="nothing":
					raise RuntimeError("Unexpected line in file")
				b.append([int(l[0],base=0),int(l[0],base=0)+int(l[1],base=0)])
	print("curr position is:")
	#print(block_current)

	print("bad blocks are:")
	#print(blocks_bad)
	return [blocks_bad,blocks_unknown]



def main():
	disk=dvd5

	# Find the capacity of the disk
	tInner=disk.tInner
	tOuter=disk.curve.findTWithGivenRadius(disk.dataRadiusOuter,NANOMETER_TO_MM/10)
	# Now, how long is the track? in mm
	tLength=disk.curve.arclengthUpTo(tOuter)-disk.curve.arclengthUpTo(tInner)
	print("Disk capacity=", disk.TToByte(tOuter))
	print("Track length(m)=", tLength/1000)

	logfile="image.log"
	blocks=parse_logfile(logfile)

	dwg=svgwrite.Drawing(filename="test.svg",debug=False)
	AXES_MAX=100;
	# We have 2 coordinate systems:
	#  * the more-or-less standard svg coordinates (origin at upper left,
	#    +x axis to the right, +y axis downward, with max axis values=AXES_MAX)
	#  * the disk coordinates, corresponding to physical measurements that could
	#    be made of the disk (origin at center of disk, +x axis to the right,
	#    +y axis upward, with the border of the svg image at exactly the disk's
	#    radius.  Basically, (x,y) means: x mm the right and y mm above the center
	#    of the disk. 
	# If we try to use SVG groups and transformations to make these
	# transformations, then we get, e.g., reflected text objects and so forth

	# SVG terminology:
	#  viewport = visible area of the SVG image (usually in pixels)
	#  viewbox = can redefine how coordinates w/o units map to the viewport
	# This sets up the SVG coordinates described above
	dwg.viewbox(0,0,AXES_MAX,AXES_MAX)

	# How to convert points and lengths from one coordinate system to another
	def svgToDisk(P):
		if isinstance(P,list):
			return list(map(svgToDisk,P))
		R=disk.radiusOuter
		return ((2*R/AXES_MAX)*P[0]-R,(2*R/AXES_MAX)*P[1]+R)
	def svgLengthToDiskLength(radius):
		return radius*(2*disk.radiusOuter/AXES_MAX)
	def diskToSvg(P):
		if isinstance(P,list):
			return list(map(diskToSvg,P))
		R=disk.radiusOuter
		return ((AXES_MAX/(2*R))*P[0]+(AXES_MAX/2),(AXES_MAX/(2*R))*P[1]+(AXES_MAX/2))
	def diskLengthToSvgLength(radius):
		return radius*(AXES_MAX/(2*disk.radiusOuter))

		
	# For debugging coord systems (coordinate system,drawing) 
	def coordTest(c,d):
		c.add(d.circle(center=(0,0),r=5,stroke='red',stroke_width=1,fill_opacity=1))
		c.add(d.circle(center=(0,0),r=100,stroke='yellow',stroke_width=1,fill_opacity=0))
		#c.add(d.path(d="M10,10 S 0 0 10 10",stroke='yellow',stroke_width=1))
		c.add(d.line(start=(-10,-10),end=(0,0),stroke='red',stroke_width=1))
		c.add(d.line(start=(-10, 10),end=(0,0),stroke='green',stroke_width=1))
		c.add(d.line(start=( 10, 10),end=(0,0),stroke='orange',stroke_width=1))
		c.add(d.line(start=( 10,-10),end=(0,0),stroke='blue',stroke_width=1))
		# Should appear at the origin, written in +x, +y directions
		c.add(d.text('Test')) 
	#coordTest(absCoords,dwg)

	# One master group, just to have no fill
	masterGroup=dwg.add(dwg.g(id='masterGroup',fill_opacity=0))

	# Border of disc
	diskBorder=masterGroup.add(dwg.g(id='diskBorder',stroke='black',stroke_width=0.5))
	diskBorder.add(dwg.circle(center=diskToSvg((0,0)),r=diskLengthToSvgLength(disk.radiusInner))) 
	diskBorder.add(dwg.circle(center=diskToSvg((0,0)),r=diskLengthToSvgLength(disk.radiusOuter))) 
	diskBorder.add(dwg.circle(center=diskToSvg((0,0)),r=diskLengthToSvgLength(disk.dataRadiusInner))) 
	diskBorder.add(dwg.circle(center=diskToSvg((0,0)),r=diskLengthToSvgLength(disk.dataRadiusOuter))) 

	# add a dot at the 'first data' point
	diskBorder.add(dwg.circle(center=diskToSvg(
		disk.curve.pos(disk.curve.findTWithGivenRadius(disk.dataRadiusInner,1/1000))),r=1))
	diskBorder.add(dwg.circle(center=diskToSvg(
		disk.curve.pos(disk.curve.findTWithGivenRadius(disk.dataRadiusOuter,1/1000))),r=1))

	# Bad areas	
	badAreas=masterGroup.add(dwg.g(id='badAreas',stroke='red',stroke_width=0.1,opacity=0.5)) #0.74*MICRON_TO_MM))
	badAreasLabels=masterGroup.add(dwg.text('',stroke='black',stroke_width=0.1,style="font-size:2px; font-family:Arial"))
	if 0==1:
		p1=dwg.path(d=curveToSVGPath(diskToSvg(disk.curve.getPoints(0,50,2)),pathType="S"),id='curve1')
		badAreas.add(p1)
		# group can contain a text, but not a textPath
		# text can contain a textPath
		badAreasLabels.add(dwg.textPath(p1,"This is a test of the emergency broadcast system and we will keep talking and talking and talking 0123456789 0123456789 0123456789"))

	for bad in blocks[0]:
		badAreas.add(dwg.path(d=curveToSVGPath(diskToSvg(disk.curve.getPoints(
			disk.byteToT(bad[0]),
			disk.byteToT(bad[1]),
			4)))))

	badAreas=masterGroup.add(dwg.g(id='badAreas',stroke='yellow',stroke_width=0.1,opacity=0.5)) #,opac0.74*MICRON_TO_MM))
	for bad in blocks[1]:
		badAreas.add(dwg.path(d=curveToSVGPath(diskToSvg(disk.curve.getPoints(
			disk.byteToT(bad[0]),
			disk.byteToT(bad[1]),
			4)))))





	print("Saving...")
	dwg.save()



if __name__ == "__main__": main()
