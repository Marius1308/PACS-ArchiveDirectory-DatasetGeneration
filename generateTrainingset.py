import os, glob,shutil, sys
import pydicom
import cv2
import numpy
import math
import copy
import random

def writeCoords(path, coords):
    with open(path, 'w') as f:
        k = 0
        for coord in coords:
            semicolon = ""
            if k != 3:
                semicolon = "\n"
            x = coord["x"]
            y = coord["y"]
            f.write(f"{x},{y}{semicolon}")
            k += 1

def readCoords(path):
    points = []
    file = open(path, 'r')
    k = 0
    for line in file.readlines():
        if k == 3:
                [x, y] = line.split(",")
        else:
            [x, y] = line[:-1].split(",")
            
        points.append({"x": int(x), "y": int(y)})
        k += 1
    return points

def default(img, coords):
    return img, coords

def flipV(img, coords):
    flipImg = numpy.flip(img, 0)
    height = len(img)
    for coord in coords:
        coord["y"] = height - coord["y"]
    return flipImg, coords

def flipH(img, coords):
    flipImg = numpy.flip(img, 1)
    width = len(img[0])
    for coord in coords:
        coord["x"] = width - coord["x"]
    return flipImg, coords


def cropImg(pixels, coords, augmentationFunction = default):

    minX = 1000
    maxX= 0
    minY= 1000
    maxY = 0

    for coord in coords:
        minX = min(minX, coord["x"])
        minY = min(minY, coord["y"])
        maxX = max(maxX, coord["x"])
        maxY = max(maxY, coord["y"])

    if(maxX-minX < maxY-minY):
        diff = (maxY-minY) - (maxX-minX)

        minX = int(minX - diff/2)
        maxX = int(maxX + diff/2)

    if(maxY-minY < maxX-minX):
        diff = (maxX-minX) - (maxY-minY)

        minY = int(minY - diff/2)
        maxY = int(maxY + diff/2)

    xBuffer = int((maxX-minX)*1.75)
    yBuffer = int((maxY-minY)*1.75)

    minX = max(0, minX-xBuffer)
    maxX = maxX+xBuffer
    minY = max(0, minY-yBuffer)
    maxY = maxY+yBuffer

    w = math.ceil((maxX-minX)/10)
    h = math.ceil((maxY-minY)/10)
    offsetX = random.randint(-w, w)
    offsetY = random.randint(-h, h)
    
    cropedImg = pixels[minY+offsetY:maxY+1+offsetY, minX+offsetX:maxX+1+offsetX]/pixels.max()

    for coord in coords:
        coord["x"] = (coord["x"] - minX - offsetX)
        coord["y"] = (coord["y"] - minY - offsetY)
    cropedImg, coords = augmentationFunction(cropedImg, coords)
    
    return cropedImg, coords


def cropAndSave(newName,newBaseDir, pixels, coords, augmentationFunction = default):
    newDcm, newCoords = cropImg(pixels, coords, augmentationFunction)
        
    cv2.imwrite(os.path.join(newBaseDir, newName + ".png"), newDcm*255)

    #Resize Image:
    img = cv2.imread(os.path.join(newBaseDir, newName + ".png"))
    res = cv2.resize(img, dsize=(250, 250), interpolation=cv2.INTER_CUBIC)
    res = numpy.asarray(res)
    for coord in coords:
        coord["x"] = int((coord["x"]) / len(img[0]) * 250)
        coord["y"] = int((coord["y"]) / len(img) * 250)
        #res[coord["y"],coord["x"]] = 255
    cv2.imwrite(os.path.join(newBaseDir, newName + ".png"), res)

    labelDir = os.path.join(newBaseDir, "label")
    os.makedirs(labelDir, exist_ok=True)
    writeCoords( os.path.join(labelDir, newName + ".txt"), newCoords)



baseDir = "V:\datasetV2-T2"
datasetDir = "V:\MLDatasetAug1"
patient_folders = [o for o in os.listdir(baseDir) if os.path.isdir(os.path.join(baseDir,o))]

sets = 0
patients = 0
for patient in patient_folders:
    folder = "train"
    if(random.random() < 0.3):
        folder = "validation"
    print(patient)
    patientPath = os.path.join(baseDir, patient)
    paths = glob.glob(os.path.join(patientPath, "**/*.txt"), recursive=True)
    for path in paths:
        newName = patient + "-" + path.split("\\")[-1][:-4]
        imagePath = path[:-6] + ".dcm"

        dcmPixels = pydicom.dcmread(imagePath).pixel_array
        coords = readCoords(path)
        if(len(coords) != 4):
            continue
        
        newBaseDir = os.path.join(datasetDir, folder)
        os.makedirs(newBaseDir, exist_ok=True)
        cropAndSave(newName, newBaseDir, numpy.ndarray.copy(dcmPixels), copy.deepcopy(coords))
        cropAndSave(newName + "-H",newBaseDir, numpy.ndarray.copy(dcmPixels), copy.deepcopy(coords), flipH)
        
    if(len(paths) > 0):
        patients += 1
    sets = sets + len(paths)


print("Total Sets:", sets)
print("Patients with sets:", patients)
print("Sets per Patient:", sets/patients)