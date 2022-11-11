import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob
import pandas as pd


baseDir = "V://datasetV2"
patient_folders = [o for o in os.listdir(baseDir) if os.path.isdir(os.path.join(baseDir,o))]

df = pd.read_csv('C:\\Users\\vpnhome06\\Documents\\IdsAll.csv')



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
    else:
        print(f"Patient {patientId} not found")

for patient in filteredPatients:
    if not patient in idList:
        continue
    
    if patient.isnumeric():
        patient = idList[patient]
    else:
        print(patient, idList[patient])

    patientPath = os.path.join(baseDir, patient)
    paths = glob.glob(os.path.join(patientPath, "**/*.dcm"), recursive=True)
    pathFound = False
    i = 0
    print("")
    for path in paths:
        dcm_file = dicom.dcmread(path)
        i = i + 1
        print(f"{i}", end = "\r")
        if "T2W" in dcm_file[0x0018, 0x1030].value and "ax" in dcm_file[0x0018, 0x1030].value:
            pathFound = True
            splitedPath = path.split("\\")
            splitedPath[0] = splitedPath[0] + "-T2"
            newPath = "\\".join(splitedPath)
            os.makedirs("\\".join(splitedPath[:-1]), exist_ok=True)
            dcm_file.save_as(newPath)
    if not pathFound:
        print(f"no T2 for: {patient}")
    

