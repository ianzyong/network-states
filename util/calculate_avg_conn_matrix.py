import numpy as np
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import pathlib

# script which takes all pickle files in the specified directories and outputs the average connectivity matrices
# also saves a csv file containing the electrodes for each patient

# CONSTANTS:
userInput = True # if True, the user will be prompted for directories and patient ids. If false, the script will automatically use "paths" and "ids" as defined below:
paths = [f"C:/Users/User/Documents/Summer 2020 Research/patientData/{filename}" for filename in sorted(os.listdir(r"C:\Users\User\Documents\Summer 2020 Research\patientData"))] # array of directories containing pickle files
ids = [filename[4:] for filename in sorted(os.listdir(r"C:\Users\User\Documents\Summer 2020 Research\patientData"))] # array of patient ids corresponding to each directory
outputFolderName = "matrices" # specify name of output folder
neverOverwrite = True # if true, the script will never ask to overwrite or overwrite existing files
askBeforeOverwrite = True # controls whether the overwrite warning is shown, only if neverOverwrite = False

parentPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data')
outputPath = os.path.join(parentPath,"{}".format(outputFolderName))

paths = ['/'.join(path.split('\\')) for path in paths] # convert path strings so they are usable

if (userInput):
    # designate path to the directory of functional connectivity pickle file(s)
    pathInput = input("Path to directory containing pickle files (if multiple, seperate with a comma): ")
    paths = pathInput.split(',') # parse input into an array of directories
    paths = ['/'.join(path.split('\\')) for path in paths] # convert path strings so they are usable
    ids = [] # initialize array
    while (len(ids) != len(paths)): # continue prompting if the number of ids does not match the number of directories provided
        idInput = input("Patient ID of directory (if multiple, seperate with a comma): ") # used for the name of the output file
        ids = idInput.split(',') # parse input into an array of ids

counter = 0
for k in range(len(paths)): # for each directory and id pair
    print(f"\nID: {ids[k]} ({k+1} of {len(ids)})") # current id
    files = os.listdir(paths[k]) # get pickle files in directory
    print(f"File(s): {files}") # print files in directory
    pickleData = [pd.read_pickle(paths[k] + "/" + x) for x in files] # unpickle functional connectivity data
    functionalArrays = [f[0:5] for f in pickleData] # take all of the numeric data
    electrodes = pickleData[0][5] # get list of electrodes from the first pickle file
    print(f"(# electrodes, # electrodes, time): {functionalArrays[0][0].shape}")
    functional = np.concatenate(functionalArrays, axis=-1) # combine arrays into one array along the time (last) axis
    averageConnectivityMatrix = np.mean(functional, axis=-1) # take average values element-wise along the time (last) axis
    print(f"Result:\n {averageConnectivityMatrix}") # print result to the console
    print(f"Shape: {averageConnectivityMatrix.shape}")
    outputFileName = f"{ids[k]}_avg_conn_matrix"
    if((f"{outputFileName}.npy" in os.listdir(outputPath))): # if a file for that patient already exists in the directory
        print("File for this patient already exists in directory.")
        if(neverOverwrite): # if neverOverwrite = True, do not save over the existing file
            print("Keeping existing file.") # the output is not saved to the directory
        elif(askBeforeOverwrite): # otherwise, if askBeforeOverwrite = True, prompt the user
            overwrite = input("Overwrite? (y/n) ").lower()
            if (overwrite == "y"):
                np.save(f"{outputPath}/{outputFileName}.npy", averageConnectivityMatrix, allow_pickle=False) # save to .npy file in the same directory
                counter += 1
                print(f"Output saved to directory as {outputFileName}.npy")
            else:
                print("Keeping existing file.") # the output is not saved to the directory
        else: # otherwise, overwrite the existing file without asking
            np.save(f"{outputPath}/{outputFileName}.npy", averageConnectivityMatrix, allow_pickle=False) # save to .npy file in the same directory
            counter += 1
            print(f"Output saved to directory as {outputFileName}.npy")   
    else: # if a file for the patient does not exist in the directory
        np.save(f"{outputPath}/{outputFileName}.npy", averageConnectivityMatrix, allow_pickle=False) # save to .npy file in the same directory
        counter += 1
        print(f"Output saved to directory as {outputFileName}.npy")
    np.savetxt(f"{outputPath}/{ids[k]}_electrodes.csv", electrodes[np.newaxis], delimiter=",", fmt = "%s") # save the electrodes as a csv file to the output directory
    print(f"Electrodes saved to directory as {ids[k]}_electrodes.csv")
print(f"{len(paths)} matrix file(s) generated and {counter} matrix file(s) saved.")
print("Done.")