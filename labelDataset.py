import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob
import pandas as pd

baseDir = "V://datasetV2-T2"
zoom = 50



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
        return max(0, self.x-zoom)
    def getZoomY(self):
        return max(0, self.y-zoom)
    def unset(self):
        self.x = None
        self.y = None
        self.isNone = True

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
plt.axis('equal')


points = []



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


def calcBiopsieCenters(dcm: dicom.FileDataset, points):
    imagePos = dcm[0x0020,0x0032].value
    imageOri = dcm[0x0020,0x0037].value
    pxSpacing = dcm[0x0028,0x0030].value
    #a= np.array([[imageOri[0]*pxSpacing[0],imageOri[3]*pxSpacing[1]], [imageOri[1]*pxSpacing[0],imageOri[4]*pxSpacing[1]]])
    #b= np.array([x-imagePos[0],y-imagePos[1]])
    #x = np.linalg.solve(a, b)
    results = []
    maxX = 0
    maxY = 0
    for point in points:
        if(maxX < point[0]/pxSpacing[0]):
            maxX = point[0]/pxSpacing[0]
        if(maxY < point[1]/pxSpacing[1]):
            maxY = point[1]/pxSpacing[1]
    for point in points:
        results.append([point[0]/pxSpacing[0] - maxX/2, point[1]/pxSpacing[1] - maxY/2, point[2]])
    return results


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
        y = iy + zoom
        x = ix + zoom
      
        
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

markers = []
def drawBioPoints(x,y):
    global ax, markers
    for marker in markers:
        marker.pop(0).remove()
    markers = []
    for center in seriesPaths[s]["coords"]:
        if center[2]:
            markers.append(ax.plot(center[0] + x, center[1]+ y, marker="o", markersize=5, markeredgecolor="none", markerfacecolor="red"))
        else:
            markers.append(ax.plot(center[0] + x, center[1] + y, marker="o", markersize=5, markeredgecolor="none", markerfacecolor="green"))

i = 1
s = 0
bx= 0
by = 0
def drawNextImage():
    global points, lines, showLines, bx, by
    path = os.path.join(seriesPaths[s]["folder"], f"{i}.dcm")
    pathLabel = os.path.join(seriesPaths[s]["folder"], f"{i}-0.txt")

    
    index= 0
    ax.clear()
    while(os.path.exists(pathLabel)):
        k = -1
        file = open(pathLabel, 'r')
        for line in file.readlines():
            k += 1

            if k == 3:
                [x, y] = line.split(",")
            else:
                [x, y] = line[:-1].split(",")
            
            points.append(Point(int(x),int(y)))
   
        index += 1
        pathLabel = os.path.join(seriesPaths[s]["folder"], f"{i}-{index}.txt")
    updateLines()

    dcm = dicom.dcmread(path)

    if(bx == 0):
        bx = len(dcm.pixel_array)/2 
    if(by == 0):
        by = len(dcm.pixel_array[0])/2

    

    drawBioPoints(bx - zoom, by - zoom)

    
    ax.set_title(str(i))

    if(zoom <= 0):
        ax.imshow(dcm.pixel_array, cmap='gray')
    else:
        ax.imshow(dcm.pixel_array[zoom:-zoom,zoom:-zoom], cmap='gray')

def removeOldFiles():
    pathLabel = os.path.join(seriesPaths[s]["folder"], f"{i}-0.txt")

    index= 0
    while(os.path.exists(pathLabel)):
        
        os.remove(pathLabel)
   
        index += 1
        pathLabel = os.path.join(seriesPaths[s]["folder"], f"{i}-{index}.txt")

def savePoints():
    global points

    removeOldFiles()

    for index in range(int(math.ceil(len(points) / 4))):
        k = -1
        pathLabel = os.path.join(seriesPaths[s]["folder"], f"{i}-{index}.txt")

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

length = 30

def on_press(event):
    global points,i,s, lines, showLines, mouseX, mouseY, zoom, bx, by
    if event.key == '1':
        removePoints()
        updateLines()
    if event.key == '2':
        zoom = 0
    if event.key == '3':
        zoom = 50
    if event.key == '4':
        zoom = 100
    if event.key == 'b':
        unset()
        if(i < length):
            i += 1
        else:
            print("Last Image")
        drawNextImage()
    if event.key == 'v':
        unset()
        if(i > 1):
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
    if event.key == 'x':
        bx = mouseX + zoom
        by = mouseY + zoom
        drawBioPoints(mouseX, mouseY)

    plt.show()

def getBioPoints(bioId):
    bioPoints = []
    df = pd.read_csv('C:\\Users\\vpnhome06\\Documents\\1600MRT.csv', on_bad_lines='skip', encoding= 'unicode_escape')

    for index, row in df.iterrows():
        values = row["1;2;3;4"].split(";")
        if(values[0] == str(bioId)):
            cancerPercent = ''.join(c for c in values[1] if c.isdigit())
            numericX = ''.join(c for c in values[2] if c.isdigit())
            numericY = ''.join(c for c in values[3] if c.isdigit())
            if(numericX == "" or numericY == "" ):
                print("-: ", len(values), numericX, numericY)
            else:
                bioPoints.append([float(numericX), float(numericY), str(cancerPercent) != "0" and str(cancerPercent).isnumeric()])
        elif(len(bioPoints) > 0):
            return bioPoints
    return bioPoints

if __name__ == "__main__":
    patient = sys.argv[1]

    if(len(sys.argv) >2):
        s = int(sys.argv[2])
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

    bioId = ""
    df = pd.read_csv('C:\\Users\\vpnhome06\\Documents\\Ids300Map.csv', on_bad_lines='skip', encoding= 'unicode_escape')
    for index, row in df.iterrows():
        values = row["1;2"].split(";")
        if values[0] == idList[patient]:
            bioId = str(values[1])
    print("bioId", bioId)

    bioPoints = []
    if(bioId != ""):
        bioPoints = getBioPoints(bioId)
        

    patientPath = os.path.join(baseDir, patient)
    paths = glob.glob(os.path.join(patientPath, "**/*.dcm"), recursive=True)
    seriesPaths = []
    j = 0
    lastFolder = ""
    for path in paths:
        j += 1
        dcm_file = dicom.dcmread(path)

        if "T2" in dcm_file[0x0018, 0x1030].value or "t2" in dcm_file[0x0018, 0x1030].value:
            folderPath = "\\".join(path.split("\\")[:-1])
            #if folderPath not in seriesPaths:
            if folderPath != lastFolder:
                lastFolder = folderPath
                print(folderPath)
                coords = calcBiopsieCenters(dcm_file, bioPoints)
                seriesPaths.append({"folder": folderPath, "coords": coords})
    drawNextImage()



    fig.canvas.mpl_connect('key_press_event', on_press)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    cid = fig.canvas.mpl_connect('motion_notify_event', onhover)

    fig.canvas.manager.window.wm_geometry("+%d+%d" % (0,0))

    plt.show()

