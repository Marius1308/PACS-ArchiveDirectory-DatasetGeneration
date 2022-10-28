import math
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import sys, os, pickle, glob

baseDir = "V://datasetV2"
patient_folders = [o for o in os.listdir(baseDir) if os.path.isdir(os.path.join(baseDir,o))]

i = 0

idList = {}
idPath = os.path.join(baseDir, "PatientIDs.pkl")
if os.path.exists(idPath):
    with open(idPath, "rb") as input_file:
        idList = pickle.load(input_file)

for patient in patient_folders:
    if not patient in idList:
        continue
    if i>3:
        continue
    i+=1

    if not patient in idList:
        print(f"Patient {patient} not found")
        sys.exit()
    
    if patient.isnumeric():
        patient = idList[patient]
    else:
        print(patient, idList[patient])

    patientPath = os.path.join(baseDir, patient)
    paths = glob.glob(os.path.join(patientPath, "**/*.dcm"), recursive=True)
    t2Paths = []
    for path in paths:
        dcm_file = dicom.dcmread(path)
        if "T2W_TSE_ax" in dcm_file[0x0018, 0x1030].value:
            splitedPath = path.split("\\")
            splitedPath[0] = splitedPath[0] + "-T2"
            newPath = "\\".join(splitedPath)
            os.makedirs("\\".join(splitedPath[:-1]), exist_ok=True)
            dcm_file.save_as(newPath)
    

