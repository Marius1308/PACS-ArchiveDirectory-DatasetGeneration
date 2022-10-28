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
        self.series[str(seriesID)] = 0

def getPatientIDs():
    return [540321]


ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
addr = ""
port = 0
assoc = ae.associate(addr, port)

studyDescriptions = []

def getStudiesForPatient(patientId):
    global assoc, studyDescriptions
    studies = {}
    ds = Dataset()
    ds.PatientID = f'{patientId}'
    ds.StudyDescription = ''
    ds.StudyDescription = ''
    #ds.StudyDescription = '%Prostata%'
    ds.Modality = ''
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
                exists = False
                if str(identifier.Modality) not in studyDescriptions:
                    studyDescriptions.append(str(identifier.Modality))
                    print(studyDescriptions)
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
        addr = "172.16.0.67"
        port = 2104
        assoc = ae.associate(addr, port)
        if assoc.is_established:
            print(f'Reconnected.')
            studies = getStudiesForPatient(patientId)
        else:
            print('Failed')
            sys.exit()
    return studies

drives= ["W:\\","X:\\","Y:\\","Z:\\"]

newRootPath = "V:\\datasetNeo"

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
            #if [0x2005, 0x140f] not in dcm:
            #    print("no Tag")
            #    return
            #if dcm[0x2005, 0x140f].value[0][0x0008, 0x9209].value == "T1":
            #    return
            os.makedirs(os.path.dirname(newPath), exist_ok=True)
            shutil.copy(path, newPath)
    if file_extension == ".tar":
        my_tar = tarfile.open(path)
        member = my_tar.getmembers()[0]
        openedTar = my_tar.extractfile(member)
        dcm = dicom.dcmread(openedTar)
        #if [0x0018, 0x1030] not in dcm:
        #    print("no Tag")
        #    return
        #if "T2W_TSE_ax" not in dcm[0x0018, 0x1030].value:
        #    return
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
            
patientsWith0= 0
patientsWith1= 0
patientsWith2= 0
patientsWith3= 0
patientsWithMore= 0
def copyImagesForPatient(patientId):
    global patientsWith0, patientsWith1, patientsWith2, patientsWith3, patientsWithMore
    studies = getStudiesForPatient(patientId)
    print(f'studies found: {len(studies)}')
    if len(studies) == 0:
        patientsWith0 += 1
    if len(studies) == 1:
        patientsWith1 += 1
    if len(studies) == 2:
        patientsWith2 += 1
    if len(studies) == 3:
        patientsWith3 += 1
    if len(studies) >= 4:
        patientsWithMore += 1
    return

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


print(f"0: {patientsWith0}")
print(f"1: {patientsWith1}")
print(f"2: {patientsWith2}")
print(f"3: {patientsWith3}")
print(f"more: {patientsWithMore}")
print("")
print(studyDescriptions)

assoc.release()
