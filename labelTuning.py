import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob
import pandas as pd

baseDir = "V://datasetV2-T2"
minX = 100
minY = 100
maxX = -100
maxY = -100



class Point:
    def __init__(self, x = None, y = None):
        self.x = x
        self.y = y
        self.isNone = True
    def set(self, x, y):
        self.x = x
        self.y = y
        self.isNone = False
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getZoomX(self):
        return max(0, self.x-minX)
    def getZoomY(self):
        return max(0, self.y-minY)
    def unset(self):
        self.x = None
        self.y = None
        self.isNone = True

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
plt.axis('equal')


points = []
paths = []



def numberOfSetPoints(points):
    i = 4
    if points[0].isNone:
        i-=1
    if points[1].isNone:
        i-=1
    if points[2].isNone:
        i-=1
    if points[3].isNone:
        i-=1
    return i

showLines = True

def plotLine(p1: Point, p2: Point, isTemp = False):
    global ax, showLines
    if not showLines:
        return None
    if isTemp:
        return ax.plot([p1.getZoomX(), p2.getZoomX()], [p1.getZoomY(), p2.getZoomY()], 'ro--', label='line 1', linewidth=1)
    return ax.plot([p1.getZoomX(), p2.getZoomX()], [p1.getZoomY(), p2.getZoomY()], 'ro-', label='line 1', linewidth=2)

def findOrthogonalPoint(xP1L, yP1L, xP2L, yP2L, xP3, yP3, length):
    xN = -(yP2L - yP1L)
    yN = (xP2L - xP1L)

    a = np.array([[xP1L - xP2L,xN], [xP1L - yP2L, yN]])
    b = np.array([xP3-xP1L, yP3-yP1L])
    x = np.linalg.solve(a, b)

    sign1 = x[0] / abs(x[0])
    sign2 = x[1] / abs(x[1])

    sign = sign1 * sign2

    t = length / math.sqrt(xN**2 + yN**2)

    xP4 = xP3 + sign * t * xN
    yP4 = yP3 + sign * t * yN

    return xP4, yP4

def getMissingPoint(p1: Point, p2:Point, p3: Point, ix, iy):
    length = math.sqrt((ix - p3.getZoomX())**2 + (iy - p3.getZoomY())**2)
    return findOrthogonalPoint(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, length)

lines = []

def removeLines():
    global lines
    for line in lines:
        line.pop(0).remove()
    lines = []

def updateLines():
    global lines, points
    
    removeLines()
   
    for i in range(int(len(points) / 2)):
        lines.append(plotLine(points[i*2], points[i*2+1]))


def removePoints():
    global points
    r = len(points) % 4
    if(r == 0 and len(points) != 0):
        r = 4
    for _ in range(r):
        points.pop()

def addPoint(ix, iy):
    global points
    startPoint = int(len(points)/4)*4
    if len(points) <= 2+(startPoint):
        y = iy + minY
        x = ix + minX
      
        
        points.append(Point(x, y))
    else:
        x, y = getMissingPoint(points[0+startPoint], points[1+startPoint], points[2+startPoint], ix, iy)
        
        points.append(Point(x, y))


def onclick(event):
    global ax, points, lines
    ix, iy = event.xdata, event.ydata
 
    addPoint(ix, iy)

    updateLines()
         
    plt.show()
    return

mouseX = 0
mouseY = 0

def onhover(event):
   global mouseX, mouseY
   mouseX = event.xdata
   mouseY = event.ydata

i = 0
bx= 0
by = 0
def drawNextImage():
    global points, lines, showLines, bx, by
    path = os.path.join(paths[i][0])
    pathLabel = os.path.join(paths[i][1])
    print(paths[i][1])

    ax.clear()
    k = -1
    file = open(pathLabel, 'r')
    for line in file.readlines():
        k += 1
        if k == 3:
            [x, y] = line.split(",")
        else:
            [x, y] = line[:-1].split(",")
        
        points.append(Point(int(x),int(y)))

    updateLines()

    dcm = dicom.dcmread(path)

    if(bx == 0):
        bx = len(dcm.pixel_array)/2 
    if(by == 0):
        by = len(dcm.pixel_array[0])/2

    
    ax.set_title(str(i))

    if(minX <= 0):
        ax.imshow(dcm.pixel_array, cmap='gray')
    else:
        ax.imshow(dcm.pixel_array[minY:maxY+1,minX:maxX+1], cmap='gray')

def removeOldFiles():
    pathLabel = os.path.join(paths[i][1])

    os.remove(pathLabel)


def savePoints():
    global points

    removeOldFiles()

    for index in range(int(math.ceil(len(points) / 4))):
        k = -1
        pathLabel = os.path.join(paths[i][1])

        with open(pathLabel, 'w') as f:
            for p in range(4):
                k += 1
                semicolon = ""
                if k != 3:
                    semicolon = "\n"
                if(p + index * 4 < len(points)):
                    f.write(f"{int(points[p + index * 4].x)},{int(points[p + index * 4].y)}{semicolon}")

def unset():
    global points
    removeLines()
    points = []


def on_press(event):
    global points,i,s, lines, showLines, mouseX, mouseY, bx, by, minX, minY, maxX, maxY
    if event.key == '1':
        removePoints()
        updateLines()
    if event.key == '2':
       
        minX = 1000
        minY = 1000
        maxX = 0
        maxY = 0
        for point in points:
            print(point.x, point.y)
            minX = min(minX, point.x)
            minY = min(minY, point.y)
            maxX = max(maxX, point.x)
            maxY = max(maxY, point.y)
        print(minX, minY, maxX, maxY)
        minX = minX - 20
        minY = minY - 20
        maxX = maxX + 20
        maxY = maxY + 20
        unset()
        drawNextImage()
    if event.key == '3':
        minX = 0
        minY = 0
        unset()
        drawNextImage()
    if event.key == '4':
        minX = 100
        minY = 100
        maxX = -100
        maxY = -100
        unset()
        drawNextImage()
    if event.key == 'b':
        unset()
        i += 1
        drawNextImage()
    if event.key == 'v':
        unset()
        if(i > 0):
            i -= 1
        else:
            print("First Image")
        drawNextImage()
    if event.key == 'a':
        savePoints()
        unset()
    if event.key == 'n':
        if showLines:
            removeLines()
            showLines = False
        else: 
            updateLines()
            showLines = True

    plt.show()



labelPaths = sorted(glob.glob(os.path.join(baseDir,"**/*.txt"), recursive=True), key=lambda x : "\\".join(["\\".join(x.split("\\")[:-1]), x.split("\\")[-1][:-6].zfill(3)]))
for path in labelPaths:
    imagePath = path[:-6] + ".dcm"
    paths.append([imagePath, path])

drawNextImage()

fig.canvas.mpl_connect('key_press_event', on_press)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid = fig.canvas.mpl_connect('motion_notify_event', onhover)
fig.canvas.manager.window.wm_geometry("+%d+%d" % (0,0))
plt.show()