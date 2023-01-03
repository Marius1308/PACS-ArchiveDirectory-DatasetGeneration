from copy import copy
import csv
from traceback import print_tb
from unittest import expectedFailure
from pynetdicom import AE
from pydicom.dataset import Dataset
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
import tarfile, os, shutil, sys, glob, pickle
import pydicom
from pydicom import  FileDataset
import pandas as pd

tags = ['AccessionNumber', 'ModalitiesInStudy', 'StudyDescription']

root = "V:\\datasetAll"

idList = {}
idPath = os.path.join(root, "PatientIDs.pkl")
if os.path.exists(idPath):
    with open(idPath, "rb") as input_file:
        idList = pickle.load(input_file)

series_meta_tags = [
    "Manufacturer",
    "InstitutionName",
    "ManufacturerModelName",
    "ProtocolName",
    "BodyPartExamined",
    "SliceThickness",
    "SpacingBetweenSlices",
    "MagneticFieldStrength",
    "RepetitionTime",
    "EchoTime",
    "NumberOfAverages",
    "ImagingFrequency",
    "ImagedNucleus",
    "NumberOfPhaseEncodingSteps",
    "EchoTrainLength",
    "PercentSampling",
    "PercentPhaseFieldOfView",
    "PixelBandwidth",
    "DeviceSerialNumber",
    "SoftwareVersions",
    "ReconstructionDiameter",
    "ReceiveCoilName",
    "TransmitCoilName",
    "AcquisitionMatrix",
    "FlipAngle",
    "PatientPosition",
    "AcquisitionDuration",
]

def getSeriesInfos(dcms):
    results = {}
    for tag in series_meta_tags:
        values = []
        for dcm in dcms:
            try:
                value = str(dcm[tag].value)
                if value not in values:
                    values.append(value)
            except:
                results[tag] = ""
        results[tag] = str(len(values))
    return results

def getSeriesInfosSimple(dcm):
    results = {}
    for tag in series_meta_tags:
        try:
            results[tag] = str(dcm[tag].value)
        except:
            results[tag] = ""
    return results

def getDcms(path):
    dcms = []
    for image in os.listdir(path):
        dcms.append(pydicom.dcmread(os.path.join(path, image)))
    return dcms

def addResluts(series_folder_path, study_results):
    dcms = []
    image = os.listdir(series_folder_path)[0]
    image_path = os.path.join(series_folder_path, image)
    if(os.path.isdir(image_path)):
        subfolders = os.listdir(series_folder_path)
        for subfolder in subfolders:
            subfolderpath = os.path.join(series_folder_path, subfolder)
            dcms = dcms + getDcms(subfolderpath)
    else:
       dcms = getDcms(series_folder_path)
    if(study_results["accession_number"] == ""):
        study_results["accession_number"] = str(dcms[0].AccessionNumber)
    if(study_results["study_description"] == ""):
        study_results["study_description"] = str(dcms[0].StudyDescription)
    tagResults = getSeriesInfos(dcms)
    tagResults["image_size"] = "0"
    study_results["series"].append(tagResults)
    return study_results

def addReslutsSimple(series_folder_path, study_results):
    image = os.listdir(series_folder_path)[0]
    image_path = os.path.join(series_folder_path, image)
    if(os.path.isdir(image_path)):
        image = os.listdir(image_path)[0]
        image_path = os.path.join(image_path, image)
    
    dcm = pydicom.dcmread(image_path)

    imageSize = os.stat(image_path).st_size / 1024

    if(study_results["accession_number"] == ""):
        study_results["accession_number"] = str(dcm.AccessionNumber)
    if(study_results["study_description"] == ""):
        study_results["study_description"] = str(dcm.StudyDescription)
    tagResults = getSeriesInfosSimple(dcm)
    tagResults["image_size"] = str(imageSize)
    study_results["series"].append(tagResults)
    return study_results

def getStudyInfos(study_folder_path):
    study_results = {
        "accession_number": "",
        "study_description": "",
        "series": []
    }
    series_folders = [o for o in os.listdir(study_folder_path) if os.path.isdir(os.path.join(study_folder_path,o))]
    for series_folder in series_folders:
        series_folder_path =  os.path.join(study_folder_path, series_folder)
        study_results = addReslutsSimple(series_folder_path, study_results)
    return study_results

def writePatientSummary(patient_id, patient_infos, output_path):
    with open(output_path, 'w', newline='') as f:
        header = (["anonymID", "patientID", "AccessionNumber", "StudyDescription"] + series_meta_tags +  ["Image Size in KB"])
        writer = csv.writer(f, delimiter =";")
        writer.writerow(header)
        for patient_info in patient_infos:
            if(patient_id.isnumeric()):
                studyData = ["-", patient_id, patient_info["accession_number"], patient_info["study_description"]]
            else:
                studyData = [patient_id, idList[patient_id], patient_info["accession_number"], patient_info["study_description"]]
            for series in patient_info["series"]:
                seriesData = [] + studyData
                for tag in series_meta_tags:
                    seriesData.append(series[tag])
                seriesData.append(series["image_size"])
                writer.writerow(map(lambda n: n.replace(".", ","), seriesData))

def writeGeneralSummary(all_patient_infos, patient_ids, output_path):
     with open(output_path, 'w', newline='') as f:
        header = (["anonymID", "patientID", "AccessionNumber", "StudyDescription"] + series_meta_tags +  ["Image Size in KB"])
        writer = csv.writer(f, delimiter =";")
        writer.writerow(header)
        for patient_id in patient_ids:
            for patient_info in all_patient_infos[patient_id]:
                if(patient_id.isnumeric()):
                    studyData = ["-", patient_id, patient_info["accession_number"], patient_info["study_description"]]
                else:
                    studyData = [patient_id, idList[patient_id], patient_info["accession_number"], patient_info["study_description"]]
                for series in patient_info["series"]:
                    seriesData = [] + studyData
                    for tag in series_meta_tags:
                        seriesData.append(series[tag])
                    seriesData.append(series["image_size"])
                    writer.writerow(map(lambda n: n.replace(".", ","), seriesData))

def getPatientInfos(patient_id):
    patient_folder_path =  os.path.join(root, patient_id)
    study_folders = [o for o in os.listdir(patient_folder_path) if os.path.isdir(os.path.join(patient_folder_path,o))]
    patient_infos = []
    for study_folder in study_folders:
        study_folder_path = os.path.join(patient_folder_path, study_folder)
        patient_infos.append(getStudyInfos(study_folder_path))
    return patient_infos


patient_folders = [o for o in os.listdir(root) if os.path.isdir(os.path.join(root,o))]

i = 0
all_patient_infos = {}
patient_ids = []
for patient_folder in patient_folders:
    i = i+1
    print(f"{i}: {patient_folder}")
    patient_folder_path =  os.path.join(root, patient_folder)
    patient_infos = getPatientInfos(patient_folder)
    if(patient_infos == None):
        continue
    
    all_patient_infos[patient_folder] = patient_infos
    patient_ids.append(patient_folder)
    writePatientSummary(patient_folder, patient_infos, os.path.join(patient_folder_path, "Summary.csv"))
    writeGeneralSummary(all_patient_infos, patient_ids, os.path.join(root, "Summary.csv"))