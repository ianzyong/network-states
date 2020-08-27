import os
import time
from download_iEEG_data import get_iEEG_data
from functional_connectivity import get_Functional_connectivity

# convert number of seconds to hh:mm:ss
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
    return f"{hours}:{minutes}:{seconds}"

# input parameters
username = input('IEEG.org username: ')
password = input('IEEG.org password: ')
iEEG_filename = input('Input iEEG_filename: ')
rid = input('Input RID: ')
start_time_usec = int(input('Input start_time_usec: '))
stop_time_usec = int(input('Input stop_time_usec: '))
removed_channels = input('Input removed_channels: ')
removed_channels = removed_channels.split(",")

# calculate duration requested an estimate the space required on disk for the eeg and functional connectivity data
total_time = (stop_time_usec - start_time_usec)//1000000
eeg_file_size = round((total_time/60)*(48962/1024**2),4)
func_file_size = eeg_file_size/2
answer = input(f"Duration requested = {convertSeconds(total_time)}. Estimated space required = {eeg_file_size} GB + {func_file_size} GB = {round(eeg_file_size + func_file_size,4)} GB.\nProceed? (y/n) ")

# download eeg data and calculate adjacency matrices
if answer == 'y' or answer == 'Y':
    parent_directory = os.path.join('gdrive','public','DATA','Human_Data','BIDS_processed')
    patient_directory = os.path.join(parent_directory,f"sub-{rid}")
    eeg_directory = os.path.join(patient_directory,'eeg')
    functional_directory = os.path.join(patient_directory,'connectivity_matrices','functional','eeg')
    # create necessary directories if they do not exist
    if not os.path.exists(patient_directory):
        os.makedirs(eeg_directory)
        os.makedirs(functional_directory)
    outputfile = os.path.join(eeg_directory,f"sub-{rid}_{iEEG_filename}_{start_time_usec}_{stop_time_usec}_EEG.pickle")
    get_iEEG_data(username, password, iEEG_filename, start_time_usec, stop_time_usec, removed_channels, outputfile)

    # start timer
    start = time.time()

    func_inputfile = outputfile
    func_outputfile = os.path.join(functional_directory,f"sub-{rid}_{iEEG_filename}_{start_time_usec}_{stop_time_usec}_functionalConnectivity.pickle")
    get_Functional_connectivity(func_inputfile,func_outputfile)

    # stop timer
    end = time.time()

    # report time elapsed for functional connectivity calculation
    print(f"Time elapsed = {convertSeconds(int(end - start))}")