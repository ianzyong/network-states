import numpy as np
import pandas as pd
from pandas.compat.pickle_compat import _class_locations_map

# backwards compatibility for pandas < 0.24
_class_locations_map.update({
        ('pandas.core.internals.managers', 'BlockManager'): ('pandas.core.internals', 'BlockManager')
        })

import os
from os import listdir
from os.path import isfile, join
import pathlib

# script which takes all pickle files in the specified directories and outputs the median connectivity matrices
# also saves a csv file containing the electrodes for each patient

# CONSTANTS:
outputFolderName = "matrices" # specify name of output folder
parentPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data')
outputPath = os.path.join(parentPath,"{}".format(outputFolderName))

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
    medianConnectivityMatrix = np.median(functional, axis=-1) # take median values element-wise along the time (last) axis
    print(f"Result:\n {medianConnectivityMatrix}") # print result to the console
    print(f"Shape: {medianConnectivityMatrix.shape}")
    outputFileName = f"{ids[k]}_median_conn_matrix"
    np.save(f"{outputPath}/{outputFileName}.npy", medianConnectivityMatrix, allow_pickle=False) # save to .npy file in the same directory
    counter += 1
    print(f"Output saved to directory as {outputFileName}.npy")
    np.savetxt(f"{outputPath}/{ids[k]}_electrodes.csv", electrodes[np.newaxis], delimiter=",", fmt = "%s") # save the electrodes as a csv file to the output directory
    print(f"Electrodes saved to directory as {ids[k]}_electrodes.csv")
print(f"{len(paths)} matrix file(s) generated and {counter} matrix file(s) saved.")
print("Done.")
