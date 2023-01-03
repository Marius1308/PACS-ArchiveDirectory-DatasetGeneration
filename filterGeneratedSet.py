import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob
import pandas as pd


baseDir = "V://datasetV2"
outputDir = "V://datasetV2-T2"
patient_folders = [o for o in os.listdir(baseDir) if os.path.isdir(os.path.join(baseDir,o))]

df = pd.read_csv('C:\\Users\\vpnhome06\\Documents\\Ids300.csv')



idList = {}
idPath = os.path.join(baseDir, "PatientIDs.pkl")
if os.path.exists(idPath):
    with open(idPath, "rb") as input_file:
        idList = pickle.load(input_file)

filteredPatients = []
for index, row in df.iterrows():
    patientId = str(row["1"])
    if patientId in idList and idList[patientId] in patient_folders:
        filteredPatients.append(idList[patientId])
    #else:
        #print(f"Patient {patientId} not found")

for patient in filteredPatients:
        

    if(os.path.isdir(os.path.join(outputDir, patient))):
        print("skip: ", patient)
        continue
    print(patient, os.path.join(outputDir, patient))

    patientPath = os.path.join(baseDir, patient)
    #paths = glob.glob(os.path.join(patientPath, "**/*.dcm"), recursive=True)

    study_folders = [o for o in os.listdir(patientPath) if os.path.isdir(os.path.join(patientPath,o))]
    pathFound = False
    i = 0
    for study in study_folders:
        studyPath = os.path.join(patientPath, study)
        series_folders = [o for o in os.listdir(studyPath) if os.path.isdir(os.path.join(studyPath,o))]
        for series in series_folders:
            seriesPath = os.path.join(studyPath, series)
            paths = glob.glob(os.path.join(seriesPath, "**/*.dcm"), recursive=True)

            isNotT2 = False
            
            for path in paths:
                if(isNotT2):
                    continue
                dcm_file = dicom.dcmread(path)
                i = i + 1
                print(f"{i}", end = "\r")

                try:
                    protocolName = dcm_file[0x0018, 0x1030].value
                except:
                    print("Wrong Format")
                    protocolName = ""

                if "T2" in protocolName and "ax" in protocolName:
                    pathFound = True
                    splitedPath = path.split("\\")
                    splitedPath[0] = splitedPath[0] + "-T2"
                    newPath = "\\".join(splitedPath)
                    os.makedirs("\\".join(splitedPath[:-1]), exist_ok=True)
                    dcm_file.save_as(newPath)
                else:
                    isNotT2 = True
    if pathFound:
        print("Found axial")
        continue
    print("General Search:")
    for study in study_folders:
        studyPath = os.path.join(patientPath, study)
        series_folders = [o for o in os.listdir(studyPath) if os.path.isdir(os.path.join(studyPath,o))]
        for series in series_folders:
            seriesPath = os.path.join(studyPath, series)
            paths = glob.glob(os.path.join(seriesPath, "**/*.dcm"), recursive=True)

            isNotT2 = False
            for path in paths:
                if(isNotT2):
                    continue
                dcm_file = dicom.dcmread(path)
                i = i + 1
                print(f"{i}", end = "\r")
                try:
                    protocolName = dcm_file[0x0018, 0x1030].value
                except:
                    print("Wrong Format")
                    protocolName = ""
                if "T2" in protocolName or "t2" in protocolName:
                    pathFound = True
                    splitedPath = path.split("\\")
                    splitedPath[0] = splitedPath[0] + "-T2"
                    newPath = "\\".join(splitedPath)
                    os.makedirs("\\".join(splitedPath[:-1]), exist_ok=True)
                    dcm_file.save_as(newPath)
                else:
                    isNotT2
    
    if not pathFound:
        print(f"no T2 for: {patient}")


