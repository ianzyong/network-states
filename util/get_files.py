import os
import sys
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
    return ":".join(str(n) for n in [hours,minutes,seconds])

if __name__ == '__main__':
    # get command line arguments
    args = str(sys.argv)
    # input parameters
    username = input('IEEG.org username: ')
    password = input('IEEG.org password: ')
    # initilize list to hold tuples corresponding to each patient
    patient_list = []
    # if there are arguments
    if len(args) > 0:
        # get the filename of the list of patients to run
        patient_metadata = args[0]
        with open(patient_metadata) as f:
            lines = [line.rstrip() for line in f]
            for k in range(0,len(lines)-4,5):
                # add patient tuple to the list
                patient_list.append(tuple([lines[k,k+4],lines[k+4].split(",")))
                
    else: # if no arguments are supplied, run just one patient
        iEEG_filename = input('Input iEEG_filename: ')
        rid = input('Input RID: ')
        start_time_usec = int(input('Input start_time_usec: '))
        stop_time_usec = int(input('Input stop_time_usec: '))
        removed_channels = input('Input removed_channels: ')
        removed_channels = removed_channels.split(",")
        patient_list.append(tuple([iEEG_filename,rid,start_time_usec,stop_time_usec,removed_channels]))

    for patient in patient_list:
        start_time_usec = patient[3]
        stop_time_usec = patient[4]
        # calculate duration requested an estimate the space required on disk for the eeg and functional connectivity data
        total_time = (stop_time_usec - start_time_usec)//1000000
        eeg_file_size = round((total_time/60)*(48962/1024**2),4)
        func_file_size = eeg_file_size/2
        print("Duration requested = {}. Estimated space required = {} GB + {} GB = {} GB.".format(convertSeconds(total_time),eeg_file_size,func_file_size,round(eeg_file_size + func_file_size,4)))
    answer = input("Proceed? (y/n) ")

    # download eeg data and calculate adjacency matrices
    if answer == 'y' or answer == 'Y':
        # start timer
        total_start = time.time()
        for patient in patient_list:
            iEEG_filename = patient[0]
            rid = patient[1]
            start_time_usec = patient[2]
            stop_time_usec = patient[3]
            removed_channels = patient[4]
            parent_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data')
            patient_directory = os.path.join(parent_directory,"sub-{}".format(rid))
            eeg_directory = os.path.join(patient_directory,'eeg')
            functional_directory = os.path.join(patient_directory,'connectivity_matrices','functional','eeg')
            # create necessary directories if they do not exist
            if not os.path.exists(patient_directory):
                os.makedirs(eeg_directory)
                os.makedirs(functional_directory)
            outputfile = os.path.join(eeg_directory,"sub-{}_{}_{}_{}_EEG.pickle".format(rid,iEEG_filename,start_time_usec,stop_time_usec))
            get_iEEG_data(username, password, iEEG_filename, start_time_usec, stop_time_usec, removed_channels, outputfile)

            # start timer
            start = time.time()

            func_inputfile = outputfile
            func_outputfile = os.path.join(functional_directory,"sub-{}_{}_{}_{}_functionalConnectivity.pickle".format(rid,iEEG_filename,start_time_usec,stop_time_usec))
            get_Functional_connectivity(func_inputfile,func_outputfile)

            # stop timer
            end = time.time()

            # report time elapsed for functional connectivity calculation
            print("Time elapsed = {}".format(convertSeconds(int(end - start))))
        total_end = time.time()
        print("{} patient(s) processed in {}.".format(len(patient_list),convertSeconds(int(total_end - total_start))))
        print("Done.")