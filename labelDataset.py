import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom

class Point:
    def __init__(self):
        self.x = None
        self.y = None
        self.isNone = True
    def set(self, x, y):
        self.x = x
        self.y = y
        self.isNone = False
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def unset(self):
        self.x = None
        self.y = None
        self.isNone = True

fig = plt.figure(figsize=(15, 10))
ax = fig.add_subplot(111)
plt.axis('equal')

coords = []

p1 = Point()
p2 = Point()
p3 = Point()
p4 = Point()


def numberOfSetPoints():
    global p1, p2, p3, p4
    i = 4
    if p1.isNone:
        i-=1
    if p2.isNone:
        i-=1
    if p3.isNone:
        i-=1
    if p4.isNone:
        i-=1
    return i

def plotLine(p1: Point, p2: Point, isTemp = False):
    global ax
    if isTemp:
        return ax.plot([p1.getX(), p2.getX()], [p1.getY(), p2.getY()], 'ro--', label='line 1', linewidth=1)
    return ax.plot([p1.getX(), p2.getX()], [p1.getY(), p2.getY()], 'ro-', label='line 1', linewidth=2)

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
    length = math.sqrt((ix - p3.x)**2 + (iy - p3.y)**2)
    return findOrthogonalPoint(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, length)

line1 = None
line2 = None

def onclick(event):
    global ax, p1, p2, p3, p4, line1, line2
    ix, iy = event.xdata, event.ydata
    print(f'x = {ix}, y = {iy}')

    global coords
    coords.append((round(ix), round(iy)))

    if p1.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p3, p4, p2, ix, iy)
        else:
            x = ix
            y = iy
        p1.set(x, y)
    elif p2.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p3, p4, p1, ix, iy)
        else:
            x = ix
            y = iy
        p2.set(x, y)
    elif p3.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p1, p2, p4, ix, iy)
        else:
            x = ix
            y = iy
        p3.set(x, y)
    elif p4.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p1, p2, p3, ix, iy)
        else:
            x = ix
            y = iy
        p4.set(x, y)

    if(line1 != None and len(line1) > 0):
        line1.pop(0).remove()
    if(line2 != None and len(line2) > 0):
        line2.pop(0).remove()
    if not (p1.isNone or p2.isNone):
        line1 = plotLine(p1, p2)
    if not (p3.isNone or p4.isNone):
        line2 = plotLine(p3, p4)
         
    plt.show()
    return
    if len(coords) == 4:
        #scal = (coords[0][0]-  coords[1][0]) * (coords[2][0]- coords[3][0]) + (coords[0][1]-  coords[1][1]) * (coords[2][1]- coords[3][1])
        #all = (coords[0][0]-  coords[1][0]) + (coords[0][1]-  coords[1][1])
        #print(scal, all)
        #xPart = (coords[0][0]-  coords[1][0]) / all
        #yPart = (coords[0][1]-  coords[1][1]) / all
#
        #newY4 = coords[3][1] + scal/((coords[0][1]-  coords[1][1]) / yPart)
        #newX4 = coords[3][0] + scal/((coords[0][0]-  coords[1][0]) / xPart)
        #print((coords[0][0]-  coords[1][0]) * (coords[2][0]- newX4) + (coords[0][1]-  coords[1][1]) * (coords[2][1]- newY4))
        #ax.plot([coords[2][0], newX4], [coords[2][1], newY4], 'go-', label='line 2', linewidth=2)
        if(lastLine != None):
            lastLine.pop(0).remove()
        length = math.sqrt((ix - coords[2][0])**2 + (iy - coords[2][1])**2)
        xP4, yP4 = findOrthogonalPoint(coords[0][0], coords[0][1], coords[1][0], coords[1][1], coords[2][0], coords[2][1], length)
        lastLine = ax.plot([coords[2][0], xP4], [coords[2][1], yP4], 'go-', label='line 2', linewidth=2)

        plt.show()
        fig.canvas.mpl_disconnect(cid)

    return coords

lastX = 0
lastY = 0

def onhover(event):
    global line1, line2, p1, p2, p3, p4, lastX, lastY
    ix, iy = event.xdata, event.ydata

    if ix is None or iy is None:
        return

    if(abs(lastX-ix) + abs(lastY-iy) < 1):
        return
    
    lastX = ix
    lastY = iy

    pTemp = Point()
   
    
    if p1.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p3, p4, p2, ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)
        
        if not p2.isNone:
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(pTemp, p2, True)
        if not (p3.isNone or p4.isNone):
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(p3, p4)
    elif p2.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p3, p4, p1, ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not p1.isNone:

            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(p1, pTemp, True)
        if not (p3.isNone or p4.isNone):
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(p3, p4)
    elif p3.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p1, p2, p4, ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not (p1.isNone or p2.isNone):
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(p1, p2)
        if not p4.isNone:
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(pTemp, p4, True)
    elif p4.isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(p1, p2, p3, ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not (p1.isNone or p2.isNone):
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(p1, p2)
        if not p3.isNone :
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(p3, pTemp, True)
    plt.show()

i = 1

def drawNextImage():
    path = f"V://datasetT2//4UMCRSXJOEEEZ3NTJYOY42D83//1.2.840.113622.6.98.37.0.3.4.1.3232.18.501750//1.3.48.670597.15.38156.5.0.5696.2017121214331068750//0//{i}.dcm"

    dcm = dicom.dcmread(path)

    ax.imshow(dcm.pixel_array)

def on_press(event):
    global p1,p2,p3,p4,i
    print('press', event.key)
    if event.key == '1':
        p1.unset()
    if event.key == '2':
        p2.unset()
    if event.key == '3':
        p3.unset()
    if event.key == '4':
        p4.unset()
    if event.key == 'd':
        i += 1
        drawNextImage()

    
    if(line2 != None and len(line2) > 0):
        line2.pop(0).remove()
    if p1.isNone or p2.isNone:
        if(line1 != None and len(line1) > 0):
            line1.pop(0).remove()
    if p3.isNone or p4.isNone:
        if(line2 != None and len(line2) > 0):
            line2.pop(0).remove()
         
    plt.show()


drawNextImage()



fig.canvas.mpl_connect('key_press_event', on_press)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid = fig.canvas.mpl_connect('motion_notify_event', onhover)

fig.canvas.manager.window.wm_geometry("+%d+%d" % (150,0))

plt.show()
