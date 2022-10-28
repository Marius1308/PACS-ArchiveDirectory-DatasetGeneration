from copy import copy
from traceback import print_tb
from pynetdicom import AE
from pydicom.dataset import Dataset
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
import tarfile, os, shutil, sys
import pydicom as dicom
import pandas as pd

class Study:
    def __init__(self, patientID, studyUID, studyDate):
        self.patientID = patientID
        self.studyUID = studyUID
        self.studyDate = studyDate
        self.series = {}
    def addSeries(self, seriesID):
        idString = str(seriesID)
        if not idString in self.series:
            self.series[str(seriesID)] = 0

def getPatientIDs():
    return [540321]


accessInfos = open('access.txt','r').readlines()

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
addr = accessInfos[0]
port = int(accessInfos[1])
assoc = ae.associate(addr, port)


def getStudiesForPatient(patientId, existingStudies = {}, studyDescription = '', modality = ''):
    global assoc
    studies = copy(existingStudies)
    ds = Dataset()
    ds.PatientID = f'{patientId}'
    ds.StudyDescription = studyDescription
    ds.Modality = modality
    ds.QueryRetrieveLevel = 'SERIES'
    ds.StudyInstanceUID = ''
    ds.SeriesInstanceUID = ''
    ds.StudyDate = ''
    if assoc.is_established:
        # Send the C-FIND request
        responses = assoc.send_c_find(
            ds, PatientRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if identifier:                
                studyUID = str(identifier.StudyInstanceUID)
                seriesUID = str(identifier.SeriesInstanceUID)
                studyDate = str(identifier.StudyDate)
                if(not studyUID in studies):
                    studies[studyUID] = Study(patientId, studyUID, studyDate)

                studies[studyUID].addSeries(seriesUID)
    else:
        print('Association rejected, aborted or never connected')
        print('Trying to reconnect')
        ae = AE()
        ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
        assoc = ae.associate(addr, port)
        if assoc.is_established:
            print(f'Reconnected.')
            studies = getStudiesForPatient(patientId, studies, studyDescription, modality)
        else:
            print('Failed')
            sys.exit()
    return studies

drives= ["W:\\","X:\\","Y:\\","Z:\\"]

newRootPath = "V:\\datasetNeoV2"

def renameDicomSeries(folder):
    for file in os.listdir(folder):
        filePath = os.path.join(folder, file)
        dcm = dicom.dcmread(filePath)
        newName = str(dcm.InstanceNumber).zfill(3)
        newFilePath = os.path.join(folder, newName)
        os.rename(filePath, newFilePath)

def newSeriesPath(seriesPath, study, seriesUID):
    seriesNumber = str(study.series[seriesUID])
    study.series[seriesUID] = study.series[seriesUID] + 1
    newPath =  os.path.join(newRootPath, study.patientID, study.studyUID, seriesUID, seriesNumber)
    return newPath

def copyFile(path, study):
    filename, file_extension = os.path.splitext(path)
    seriesUID = None
    if file_extension == ".dcm":
        dcm = dicom.dcmread(path)
        seriesUID = dcm.SeriesInstanceUID
        if seriesUID in study.series:
            newPath = newSeriesPath(path, study, seriesUID)
            newPath += ".dcm"
            os.makedirs(os.path.dirname(newPath), exist_ok=True)
            shutil.copy(path, newPath)
    if file_extension == ".tar":
        my_tar = tarfile.open(path)
        member = my_tar.getmembers()[0]
        openedTar = my_tar.extractfile(member)
        dcm = dicom.dcmread(openedTar)
        seriesUID = dcm.SeriesInstanceUID
        if seriesUID in study.series:
            newPath = newSeriesPath(path, study, seriesUID)
            my_tar.extractall(newPath)
        my_tar.close()

def getStudieFolder(study):
    year = (study.studyDate)[0:4]
    month = (study.studyDate)[4:6]
    day = (study.studyDate)[6:8]
    folders = []
    for drive in drives:
        path = os.path.join(drive,"Archived", year, month,day, study.patientID)
        if(os.path.isdir(path)):
            folders.append(path)

    return folders
            

def copyImagesForPatient(patientId):
    global patientsWith0, patientsWith1, patientsWith2, patientsWith3, patientsWithMore, modalities, i, pIDsAll
    studies = {}
    studies = getStudiesForPatient(patientId, studyDescription="%Abdomen%", modality="MR")
    studies = getStudiesForPatient(patientId, existingStudies=studies, studyDescription="%Prost%", modality="MR")
    studies = getStudiesForPatient(patientId, existingStudies=studies, studyDescription="%prost%", modality="MR")
    studies = getStudiesForPatient(patientId, existingStudies=studies, studyDescription="%PROST%", modality="MR")
    studies = getStudiesForPatient(patientId, existingStudies=studies, studyDescription="%Becken%", modality="MR")
    studies = getStudiesForPatient(patientId, existingStudies=studies, studyDescription="%BECKEN%", modality="MR")

    for s in studies:
        study = studies[s]
        for folder in getStudieFolder(study):
            for element in os.scandir(folder):
                name = element.name
                elementPath = os.path.join(folder, name)
                copyFile(elementPath, study)



df = pd.read_csv('C:\\Users\\vpnhome06\\Documents\\IdsNeo.csv')

for index, row in df.iterrows():
    patientId = str(row["1"])
    print(f'patient: {patientId} ({index})')
    copyImagesForPatient(patientId)


assoc.release()
