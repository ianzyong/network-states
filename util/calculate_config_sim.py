# import modules
import sys
import os
import os.path
import time
try:
   import cPickle as pickle
except:
   import pickle
import numpy as np
from scipy.special import comb
from scipy import stats
import pandas as pd
import re

def convertSeconds(time): 
    seconds = time % 3600 
    hours = time // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if seconds < 10:
        seconds = "0" + str(seconds)
    if minutes < 10:
        minutes = "0" + str(minutes)
    if hours < 10:
        hours = "0" + str(hours)
    return ":".join(str(n) for n in [hours,minutes,seconds])

pickle_dir = input('Path to folder containing pickle files: ')
# band to run calculations on
band = int(input('Which band? (0-4) ')) 
output_filename = input('Name of output file: ')
files = os.listdir(pickle_dir)

# directory to save results
save_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'notebooks',output_filename)

# only consider pickle files
k = 0
while k < len(files):
    if files[k][-7:] != ".pickle":
        files.pop(k)
    else:
        k = k+1

# get start times
start_times = [int(re.findall(r'[0-9]+', f)[2]) for f in files]
sorted_times = sorted(start_times)
formatted_time_in_order = [convertSeconds(int(time/1000000)-1) for time in sorted_times]

# sort files by start time
sorted_files = [x for _,x in sorted(zip(start_times,files))]

# load in connectivity matrices 
pickle_data = [pd.read_pickle("{}/{}".format(pickle_dir,f)) for f in sorted_files]

for k in range(len(pickle_data)):
        pickle_data[k][band] = np.moveaxis(pickle_data[k][band],-1,0) # make the first axis the time axis

print("Pickle files loaded and read.")

patient_matrices = pickle_data[0][band]
for k in range(1,len(pickle_data)):
    patient_matrices = np.concatenate((patient_matrices,pickle_data[k][band]))

# calculate network configuration matrix
# initialize matrix
network_config = np.zeros((int(comb(patient_matrices[0,:,:].shape[1],2))),)

for k in range(len(patient_matrices)):
    # calculate configuration for one time window
    # initialize array
    frame_config = np.zeros(1,)
    for m in range(patient_matrices[k].shape[1]):
        frame_config = np.hstack((frame_config,patient_matrices[k][m][m+1:]))
    # strip leading zero
    frame_config = frame_config[1:]   
    # append to network config matrix
    network_config = np.vstack((network_config, frame_config))
# remove junk data
network_config = network_config[1:][:]

# configuration similarity matrix
config_sim = np.zeros((network_config.shape[0],network_config.shape[0]))

# start timer
start = time.time()

for k in range(network_config.shape[0]):
    for m in range(k+1,network_config.shape[0]):
        config_sim[k,m] = stats.pearsonr(network_config[k,:],network_config[m,:])[0]
config_sim = config_sim + config_sim.T + np.identity(network_config.shape[0])

# end timer
end = time.time()

np.save(save_directory,config_sim)

print("Done. Result:")
print(config_sim)
print("Time elapsed: {}.".format(convertSeconds(int(end - start))))
