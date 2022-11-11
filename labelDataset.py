import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob

baseDir = "V://datasetV2"



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

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
plt.axis('equal')

coords = []

points = [Point(), Point(), Point(), Point()]



def numberOfSetPoints():
    global points
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
    print("plotLine")
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
    global ax, points, line1, line2
    ix, iy = event.xdata, event.ydata
    print(f'x = {ix}, y = {iy}')

    global coords
    coords.append((round(ix), round(iy)))

    if points[0].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[2], points[3], points[1], ix, iy)
        else:
            x = ix
            y = iy
        points[0].set(x, y)
    elif points[1].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[2], points[3], points[0], ix, iy)
        else:
            x = ix
            y = iy
        points[1].set(x, y)
    elif points[2].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[0], points[1], points[3], ix, iy)
        else:
            x = ix
            y = iy
        points[2].set(x, y)
    elif points[3].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[0], points[1], points[2], ix, iy)
        else:
            x = ix
            y = iy
        points[3].set(x, y)

    if(line1 != None and len(line1) > 0):
        line1.pop(0).remove()
    if(line2 != None and len(line2) > 0):
        line2.pop(0).remove()
    if not (points[0].isNone or points[1].isNone):
        line1 = plotLine(points[0], points[1])
    if not (points[2].isNone or points[3].isNone):
        line2 = plotLine(points[2], points[3])
         
    plt.show()
    return

lastX = 0
lastY = 0

def onhover(event):
    global line1, line2, points, lastX, lastY
    ix, iy = event.xdata, event.ydata

    if ix is None or iy is None:
        return

    if(abs(lastX-ix) + abs(lastY-iy) < 1):
        return
    
    lastX = ix
    lastY = iy

    pTemp = Point()
   
    
    if points[0].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[2], points[3], points[1], ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)
        
        if not points[1].isNone:
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(pTemp, points[1], True)
        if not (points[2].isNone or points[3].isNone):
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(points[2], points[3])
    elif points[1].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[2], points[3], points[0], ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not points[0].isNone:

            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(points[0], pTemp, True)
        if not (points[2].isNone or points[3].isNone):
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(points[2], points[3])
    elif points[2].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[0], points[1], points[3], ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not (points[0].isNone or points[1].isNone):
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(points[0], points[1])
        if not points[3].isNone:
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(pTemp, points[3], True)
    elif points[3].isNone:
        if numberOfSetPoints() == 3:
            x, y = getMissingPoint(points[0], points[1], points[2], ix, iy)
        else:
            x = ix
            y = iy
        pTemp.set(x, y)

        if not (points[0].isNone or points[1].isNone):
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            line1 = plotLine(points[0], points[1])
        if not points[2].isNone :
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            line2 = plotLine(points[2], pTemp, True)
    plt.show()

i = 1
s = 0

def drawNextImage():
    global points, line1, line2, showLines
    path = os.path.join(seriesPaths[s], f"{i}.dcm")
    pathLabel = os.path.join(seriesPaths[s], f"{i}.txt")

    k = -1
    if os.path.exists(pathLabel):
        file = open(pathLabel, 'r')
        lines = file.readlines()
        for line in lines:
            k += 1

            if k == 3:
                [x, y] = line.split(",")
            else:
                [x, y] = line[:-1].split(",")
            
            print(x, y)
            points[k].set(int(x),int(y))

    if k == 3:
        line1 = plotLine(points[0], points[1])
        line2 = plotLine(points[2],  points[3])
    dcm = dicom.dcmread(path)

    ax.set_title(str(i))
    ax.imshow(dcm.pixel_array, cmap='gray')

def savePoints():
    global points
    pathLabel = os.path.join(seriesPaths[s], f"{i}.txt")
    k = -1
    with open(pathLabel, 'w') as f:
        for point in points:
            k += 1
            semicolon = ""
            if k != 3:
                semicolon = "\n"
            f.write(f"{int(point.x)},{int(point.y)}{semicolon}")
    print("saved")

def unset():
    global points, line1, line2
    if(line1 != None and len(line1) > 0):
        line1.pop(0).remove()
    if(line2 != None and len(line2) > 0):
        line2.pop(0).remove()
    for i in [0,1,2,3]:
        points[i].unset()

def on_press(event):
    global points,i,s, line1, line2, showLines
    print('press', event.key)
    if event.key == '1':
        points[0].unset()
    if event.key == '2':
        points[1].unset()
    if event.key == '3':
        points[2].unset()
    if event.key == '4':
        points[3].unset()
    if event.key == 'b':
        unset()
        if(i < 24):
            i += 1
        elif len(seriesPaths) > s+1:
            s += 1
            i = 1
        else:
            print("Last Image")
        drawNextImage()
    if event.key == 'v':
        unset()
        if(i > 1):
            i -= 1
        elif s > 0:
            s -= 1
            i = 24
        else:
            print("First Image")
        drawNextImage()
    if event.key == 'a':
        savePoints()
        unset()
    if event.key == 'n':
        if showLines:
            if(line1 != None and len(line1) > 0):
                line1.pop(0).remove()
            if(line2 != None and len(line2) > 0):
                line2.pop(0).remove()
            showLines = False
        else: 
            if not (points[0].isNone or points[1].isNone):
                line1 = plotLine(points[0], points[1])
            if not (points[2].isNone or points[3].isNone) :
                line2 = plotLine(points[2], points[3])
            showLines = True
        plt.show()


    
    if points[0].isNone or points[1].isNone:
        if(line1 != None and len(line1) > 0):
            line1.pop(0).remove()
    if points[2].isNone or points[3].isNone:
        if(line2 != None and len(line2) > 0):
            line2.pop(0).remove()
         
    plt.show()


if __name__ == "__main__":
    patient = sys.argv[1]

    idList = {}

    idPath = os.path.join("V://datasetV2", "PatientIDs.pkl")
    if os.path.exists(idPath):
        with open(idPath, "rb") as input_file:
            idList = pickle.load(input_file)

    if not patient in idList:
        print(f"Patient {patient} not found")
        sys.exit()
    if patient.isnumeric():
        patient = idList[patient]

    print(patient, idList[patient])

    patientPath = os.path.join(baseDir, patient)
    paths = glob.glob(os.path.join(patientPath, "**/*.dcm"), recursive=True)
    seriesPaths = []
    j = 0
    for path in paths:
        print(j)
        j += 1
        dcm_file = dicom.dcmread(path)
        if "T2W_TSE_ax" in dcm_file[0x0018, 0x1030].value:
            folderPath = "\\".join(path.split("\\")[:-1])
            print(folderPath)
            if folderPath not in seriesPaths:
                seriesPaths.append(folderPath)
    
    drawNextImage()



    fig.canvas.mpl_connect('key_press_event', on_press)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    #cid = fig.canvas.mpl_connect('motion_notify_event', onhover)

    fig.canvas.manager.window.wm_geometry("+%d+%d" % (0,0))

    plt.show()

