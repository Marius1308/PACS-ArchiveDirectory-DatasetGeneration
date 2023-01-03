# MRT Extraction from PACS Archiv Server and Labeling with Biopsie Data
Autor: Marius Schmitz

## Content: 
This Reposotory contains Python Scripts to find Patients in the PACS System and to extract Images from a PACS Archive Server. It also provides Scripts to generate Label, for RESIST Markers and a Script to create a Summary of Meta Data information in an Excel Tabel.

## generate.py
Image Extraction
### Input (change Paths inside Code): 
1. .txt File with IP and Port of the PACS Server
2. .csv File with patient Ids
3. output directory
### Output:
A Directory with subdierctories for each Patient
### Note:
You can filter the images before extraction with modifications inside the 'copyImagesForPatient' Methode.

## generateStudySummary.py
Generates Metadata summary
### Input (change Paths inside Code): 
1. Folder structure like the output of 'generate.py'
2. output directory
### Output:
A Excel File with columns for each Series of all Patients 
### Note:
Change used Tags in the 'series_meta_tags' list

## labelDataset.py
A tool to label a Series of MRT images with RESIST markers 
### Input (change Paths inside Code): 
1. Folder with only .dcm files 
2. output directory
3. A Patient Id as Param when calling the script
4. File with Biopsie Data
### Output:
.txt files with markers
### Note:
The Biopsie Data is shown in the Tool and can help while labeling the images. To Navigate inside the tool use keys listed inside 'on_press' methode.