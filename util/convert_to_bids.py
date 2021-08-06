import sys
import os
import os.path as op
import shutil
from pprint import pprint
sys.path.append('../../ieegpy/ieeg')
from ieeg.auth import Session
import pandas as pd
import pickle
from pybv import write_brainvision
import numpy as np
import mne
from mne_bids import (write_raw_bids, BIDSPath, read_raw_bids, print_dir_tree)
import time
from download_iEEG_data import get_iEEG_data
import pyedflib
from scipy.io import loadmat
from pathlib import Path

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

mat_str = input('Input path to localization .mat file: ')
mat_path = Path(mat_str)
mat = loadmat(mat_path)
localization = mat['patient_localization']

def generate_electrode_dict(portal_labels, labels):
    label_dict = {}
    for label in labels:
        if label in portal_labels:
            label_dict[label] = label
        else:
            for i, c in enumerate(label):
                if c.isdigit():
                    break
            padded_num = label[i:].zfill(2)
            padded_name = label[0:i] + padded_num
            if padded_name in portal_labels:
                label_dict[label] = padded_name
            elif "EEG {} {}-Ref".format(label[0:i],padded_num) in portal_labels:
                label_dict[label] = "EEG {} {}-Ref".format(label[0:i],padded_num)
            elif "EEG {}-Ref".format(label) in portal_labels:
                label_dict[label] = "EEG {}-Ref".format(label)
            else:
                print("Warning: could not resolve electrode label {}.".format(label))
                label_dict[label] = label
    return label_dict

# download ieeg data from ieeg.org
if __name__ == '__main__':
    # input parameters
    username = input('IEEG.org username: ')
    password = input('IEEG.org password: ')
    overwrite_files = input("Overwrite existing .edf files? (y/n) ")
    overwrite_files = (overwrite_files == "y" or overwrite_files == "Y")
    redownload = input("Overwrite existing .pickle files? (y/n) ")
    redownload = (redownload == "y" or redownload == "Y")
    print(redownload)
    # initilize list to hold tuples corresponding to each patient
    patient_list = []
    # if there are arguments
    if len(sys.argv) > 1:
        # get the filename of the list of patients to run
        patient_metadata = sys.argv[1]
        with open(patient_metadata) as f:
            lines = [line.rstrip() for line in f]
            for k in range(0,len(lines)-4,5):
                # add patient tuple to the list
                patient_list.append(tuple(lines[k:k+5]))
                
    else: # if no arguments are supplied, run just one patient
        iEEG_filename = input('Input iEEG_filename: ')
        rid = input('Input RID: ')
        start_time_usec = int(input('Input start_time_usec: '))
        stop_time_usec = int(input('Input stop_time_usec: '))
        removed_channels = input('Input removed_channels: ')
        #removed_channels = removed_channels.split(",")
        patient_list.append(tuple([iEEG_filename,rid,start_time_usec,stop_time_usec,removed_channels]))

    total_size = 0
    for patient in patient_list:
        start_time_usec = int(patient[2])
        stop_time_usec = int(patient[3])
        # calculate duration requested an estimate the space required on disk for the eeg and functional connectivity data
        total_time = (stop_time_usec - start_time_usec)//1000000
        eeg_file_size = round((total_time/60)*(48962/1024**2),4)
        print("{}:".format(patient[1]))
        print("Duration requested = {}. Estimated space required = {} GB".format(convertSeconds(total_time),eeg_file_size))
        total_size = total_size + eeg_file_size
    print("Total estimated space required = {} GB.".format(round(total_size,4)))
    print("Total number of intervals requested = {}".format(len(patient_list)))
    answer = input("Proceed? (y/n) ")

    # download eeg data
    if answer == 'y' or answer == 'Y':
        process_count = 0
        # start timer
        total_start = time.time()
        for patient in patient_list:
            iEEG_filename = patient[0]
            interval_name = patient[1]
            rid = interval_name.partition("_")[0]
            acq = interval_name.split("_")[3].partition("-")[-1]
            task = interval_name.split("_")[2].partition("-")[-1]
            run = interval_name.split("_")[4].partition("-")[-1]
            start_time_usec = patient[2]
            stop_time_usec = patient[3]
            removed_channels = patient[4].split(",")
            parent_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data')
            patient_directory = os.path.join(parent_directory,"sub-{}".format(rid))
            eeg_directory = os.path.join(patient_directory,'eeg')

            # create necessary directories if they do not exist
            if not os.path.exists(patient_directory):
                os.makedirs(eeg_directory)
            outputfile = os.path.join(eeg_directory,"sub-{}_{}_{}_{}_EEG.pickle".format(rid,iEEG_filename,start_time_usec,stop_time_usec))
            
            bids_root = os.path.join(parent_directory,'bids_output')            
            
            edf_filename = os.path.join(bids_root,"sub-{}".format(rid),"ses-presurgery","ieeg","sub-{}.edf".format(interval_name))

            if overwrite_files or not os.path.isfile(edf_filename):

                # download data if the file does not already exist
                #if not os.path.isfile(outputfile):

                # start timer
                start = time.time()
                    
                try:
                    true_ignore_electrodes = get_iEEG_data(username, password, iEEG_filename, start_time_usec, stop_time_usec, removed_channels, outputfile, get_all_channels = True, redownload = redownload)
                except KeyError:
                    print("Encountered KeyError: ignore_electrodes are probably named differently on ieeg.org. Skipping...")
                    continue
                except KeyboardInterrupt:
                    print('Interrupted')
                    try:
                        sys.exit()
                    except SystemExit:
                        os._exit()

                # stop timer
                end = time.time()

                # report time elapsed
                print("Time elapsed = {}".format(convertSeconds(int(end - start))))
                        
                #else:
                #    print("{} exists, skipping...".format(outputfile))

                try:
                    pickle_data = pd.read_pickle(outputfile)
                except FileNotFoundError:
                    print("Pickle data not found, skipping...")
                    continue

                signals = np.transpose(pickle_data[0].to_numpy())
                fs = pickle_data[1]

                s = Session(username, password)
                ds = s.open_dataset(iEEG_filename)
                channel_names = ds.get_channel_labels()

                #channel_names = [x for x in channel_names if (x not in removed_channels) and (x not in formatted_channels)]
                
                # TODO: write interval in BrainVision format

                #write_brainvision(data=signals, sfreq=fs, ch_names=channel_names, fname_base=fname, folder_out=tmpdir,events=events)

                # write interval to an edf file
                
                signal_headers = pyedflib.highlevel.make_signal_headers(channel_names, physical_min=-50000, physical_max=50000, transducer=acq)
                #sample_rate = ds.sample_rate
                header = pyedflib.highlevel.make_header(patientname=rid)

                # edf_file = os.path.join(patient_directory,"sub-{}_{}_{}_{}_EEG.edf".format(rid,iEEG_filename,start_time_usec,stop_time_usec))
                edf_file = os.path.join(patient_directory,"{}.edf".format(interval_name))
                try:
                    pyedflib.highlevel.write_edf(edf_file, signals, signal_headers, header)
                except AssertionError as err:
                    print(err)
                    print("Failed to write {}, skipping...".format(edf_file))
                    continue
                
                coord_arr = localization[localization['patient'] == rid]["coords"][0]
                coord_arr = [list(item.astype(float)) for item in coord_arr]
                label_arr = localization[localization['patient'] == rid]["labels"][0]
                label_arr = [item[0] for item in label_arr[:,0]]

                # create label dictionary
                label_dict = generate_electrode_dict(channel_names, label_arr)

                # apply label dictionary
                true_label_arr = [label_dict[label] for label in label_arr]

                zi = list(zip(true_label_arr,coord_arr))

                # make montage
                montage = mne.channels.make_dig_montage(ch_pos=dict(zi),coord_frame="mni_tal")
                print(f'Created {len(dict(zi))} channel positions:')
                print(dict(zi))

                # convert to BIDS format and save
                raw = mne.io.read_raw_edf(edf_file)

                raw.info['line_freq'] = 60 # power line frequency

                # set channel types
                raw.set_channel_types({ch: acq for ch in raw.ch_names})

                # set bad electrodes
                raw.info['bads'].extend(true_ignore_electrodes)

                # set montage
                raw.set_montage(montage, on_missing='warn')

                # create necessary directories if they do not exist
                if not os.path.exists(bids_root):
                    os.makedirs(bids_root)
                
                bids_path = BIDSPath(subject=rid, root=bids_root, session="presurgery", task=task, acquisition=acq, run=run, datatype='ieeg')

                write_raw_bids(raw, bids_path, overwrite=True)
                
                print("Saved BIDS-formatted interval for {} to {}.".format(rid,bids_root))
                
                process_count = process_count + 1
            
            else:
                print("BIDS-formatted interval for {} already exists at {}, skipping...".format(rid,edf_filename))

        total_end = time.time()
        print("{}/{} intervals(s) processed in {}.".format(process_count,len(patient_list),convertSeconds(int(total_end - total_start))))
        print("Done.")
