# import modules
import sys
import os
import os.path
import time
import statistics
try:
   import cPickle as pickle
except:
   import pickle
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.pyplot import savefig
#import seaborn as sns
import re
from scipy import signal, integrate, io, stats
from scipy.fft import fft, fftfreq
import math
import matlab
import matlab.engine
from datetime import date
from datetime import datetime

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

# definitions for filters
def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def notch(rem, Q, fs):
    nyq = 0.5 * fs
    w0 = rem / nyq
    b, a = signal.iirnotch(w0, Q, fs)
    return b, a

def notch_filter(data, rem, Q, fs):
    b, a = notch(rem, Q, fs)
    y = signal.lfilter(b, a, data)
    return y

# get date
today = date.today()
date_today = today.strftime("%Y-%m-%d")

# get time
now = datetime.now()
current_time = now.strftime("%H.%M.%S")

pickle_paths = ["foo"]
ids = ["foo","bar"]
while len(pickle_paths) != len(ids):
    # prompt for path to pickle files
    pickle_paths = str(input('Enter path(s) to pickle files, seperated by commas: '))
    ids = str(input('Enter patient IDs, seperated by commas: '))

    # turn input into lists
    pickle_paths = pickle_paths.split(",")
    ids = ids.split(",")

# get multiplier values
w_multiplier = float(input('w_multiplier: '))
n2_multiplier = float(input('n2_multiplier: '))
n3_multiplier = float(input('n3_multiplier: '))

for k in range(len(pickle_paths)):
    patient_id = ids[k]
    print(f"Obtaining sleep stage predictions for {patient_id}... ({k+1} of {len(pickle_paths)})")
    pickle_dir = pickle_paths[k]
    files = os.listdir(pickle_dir)

    # get start times
    start_times = [int(re.findall(r'[0-9]+', f)[2]) for f in files]
    sorted_times = sorted(start_times)
    formatted_time_in_order = [convertSeconds(int(time/1000000)-1) for time in sorted_times]

    # sort files by start time
    sorted_files = [x for _,x in sorted(zip(start_times,files))]

    # load in connectivity matrices 
    pickle_data = [pd.read_pickle("{}/{}".format(pickle_dir,f)) for f in sorted_files]

    # sampling rate of ieeg.org data
    fs = 512

    # convert referential montages to bipolar montages

    bipolar_data = []

    for segment in pickle_data:
        segment_data = segment[0]
        bipolar_channels = []
        for label in segment_data.columns:
            electrode_num = "".join(re.findall(r'[0-9]', label))
            electrode_letters = "".join(re.findall(r'[a-zA-Z]', label))
            num_digits = len(electrode_num)
            electrode_int = int(electrode_num)
            pair_int = electrode_int + 1
            pair_num = str(pair_int)
            while len(pair_num) < len(electrode_num):
                pair_num = "0" + pair_num
            pair_label = electrode_letters + pair_num
            if pair_label in segment_data.columns and electrode_letters != "EKG":
                raw_bipolar = segment_data[label]-segment_data[pair_label];
                # apply filters to raw bipolar montage data
                # bandpass from 0.5 to 80 Hz
                filtered_bipolar = butter_bandpass_filter(raw_bipolar, 0.5, 80, fs, order=6)
                # notch filter at 60 Hz
                filtered_bipolar = notch_filter(filtered_bipolar, 60, 0.99, fs)
                # downsample signal to 200 Hz
                filtered_bipolar = signal.resample(filtered_bipolar, num=30*200)
                bipolar_channels.append(filtered_bipolar)
        bipolar_data.append(bipolar_channels)

    # load in MATLAB predictor
    eng = matlab.engine.start_matlab()
    #model = io.loadmat("tc.mat")
    struct = eng.load("/gdrive/public/USERS/ianzyong/network-states/notebooks/tc.mat")
    eng.workspace["predictFcn"] = struct['trainedClassifier']['predictFcn']

    segment_predictions = []

    # obtain data to make predictions
    # for each segment
    for segment in bipolar_data:
        channel_predictions = []
        # for each channel
        for channel in segment:
            # arrays to store band power
            dp = []
            tp = []
            ap = []
            bp = []
            gp = []
            # for each 6-second-long subsegment
            for sub_start in range(0,30*200,6*200):
                sub_segment = channel[sub_start:sub_start+(6*200)]
                # get spectral density
                [f, spec_dens] = signal.welch(sub_segment,fs=200,nperseg=400,noverlap=200,nfft=400)
                # normalize spectral density
                int_res = integrate.cumtrapz(spec_dens, f)
                total_area = int_res[-1]
                spec_dens = spec_dens/total_area
                
                temp_spec = np.array(spec_dens)
                temp_f = np.array(f)
                # get band power
                int_res = integrate.cumtrapz(temp_spec[np.bitwise_and(temp_f>=0.5,temp_f<4)],temp_f[np.bitwise_and(temp_f>=0.5,temp_f<4)])
                dp.append(int_res[-1])
                int_res = integrate.cumtrapz(temp_spec[np.bitwise_and(temp_f>=4,temp_f<8)],temp_f[np.bitwise_and(temp_f>=4,temp_f<8)])
                tp.append(int_res[-1])
                int_res = integrate.cumtrapz(temp_spec[np.bitwise_and(temp_f>=8,temp_f<13)],temp_f[np.bitwise_and(temp_f>=8,temp_f<13)])
                ap.append(int_res[-1])
                int_res = integrate.cumtrapz(temp_spec[np.bitwise_and(temp_f>=13,temp_f<30)],temp_f[np.bitwise_and(temp_f>=13,temp_f<30)])
                bp.append(int_res[-1])
                int_res = integrate.cumtrapz(temp_spec[np.bitwise_and(temp_f>=30,temp_f<80)],temp_f[np.bitwise_and(temp_f>=30,temp_f<80)])
                gp.append(int_res[-1])
                
            band_data = [statistics.mean(dp).item(), statistics.mean(tp).item(), statistics.mean(ap).item(), statistics.mean(bp).item(), statistics.mean(gp).item(), statistics.variance(dp).item(), statistics.variance(tp).item(), statistics.variance(ap).item(), statistics.variance(bp).item(), statistics.variance(gp).item(), (max(dp)-min(dp)).item(), (max(tp)-min(tp)).item(), (max(ap)-min(ap)).item(), (max(bp)-min(bp)).item(), (max(gp)-min(gp)).item()]
            if any(math.isnan(x) for x in band_data):
                channel_predictions.append("NaN")
            else:
                eng.workspace["band_data"] = band_data
                eng.workspace["band_data"] = eng.eval("cell2table(band_data)")
                eng.workspace["band_data"] = eng.eval("renamevars(band_data,[\"band_data1\",\"band_data2\",\"band_data3\",\"band_data4\",\"band_data5\",\"band_data6\",\"band_data7\",\"band_data8\",\"band_data9\",\"band_data10\",\"band_data11\",\"band_data12\",\"band_data13\",\"band_data14\",\"band_data15\"],[\"MeanDeltaBandPower\",\"MeanThetaBandPower\",\"MeanAlphaBandPower\",\"MeanBetaBandPower\",\"MeanGammaBandPower\",\"DeltaBandPowerVariance\",\"ThetaBandPowerVariance\",\"AlphaBandPowerVariance\",\"BetaBandPowerVariance\",\"GammaBandPowerVariance\",\"DeltaBandPowerRange\",\"ThetaBandPowerRange\",\"AlphaBandPowerRange\",\"BetaBandPowerRange\",\"GammaBandPowerRange\"])")
                channel_predictions.append(eng.eval("string(predictFcn(band_data))"))
        
        # adjust channel predictions to favor W and N3 stages
        num_W = channel_predictions.count("W")
        num_N2 = channel_predictions.count("N2")
        num_N3 = channel_predictions.count("N3")
        for k in range(int(round(num_W*(w_multiplier-1)))):
            channel_predictions.append("W")
        for k in range(int(round(num_N2*(n2_multiplier-1)))):
            channel_predictions.append("N2")
        for k in range(int(round(num_N3*(n3_multiplier-1)))):
            channel_predictions.append("N3")
        segment_predictions.append(stats.mode(channel_predictions))
        
    prediction_text = [x[0][0] for x in segment_predictions]
    prediction_text = [float(x.replace("W","1").replace("N2","0").replace("N3","-1")) for x in prediction_text]

    # save results to file
    pred_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data','sleep_predictions',f"{patient_id}_predictions.npy")
    np.save(pred_directory,prediction_text)
        
    # output plot
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), dpi=100)

    # plot segment predictions
    t = range(0,4*24*60,5)
    axs[0].scatter(t,prediction_text,50,marker="|")
    axs[0].set_yticks([-1, 0, 1])
    axs[0].set_yticklabels(["N3","N2","W"])
    axs[0].set_title(f"Sleep Stage Predictions ({patient_id})")
    axs[0].set_xticks(range(0,24*60*4+1,int(24*60/2)))
    axs[0].set_xticklabels(["0","0.5","1","1.5","2","2.5","3","3.5","4"])
    axs[0].set_xlabel("Days elapsed")
    axs[0].set_ylabel("Prediction")

    # replace NaN values with preceding prediction value
    for k in range(0,len(prediction_text)):
        if math.isnan(prediction_text[k]):
            prediction_text[k] = prediction_text[k-1]

    # fft
    N = len(prediction_text)
    T = 5*60
    yf = fft(prediction_text)
    xf = fftfreq(N, T)[:N//2]
    axs[1].plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    axs[1].set_title(f"FFT of Prediction Data ({patient_id})")
    axs[1].set_xlim([0, 10*(1/86400)])
    axs[1].set_xlabel("Frequency (Hz)")
    axs[1].set_ylabel("Magnitude")
    fig.tight_layout()

    # save figure to disk
    output_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'data','sleep_predictions',f'Wx{w_multiplier}_N2x{n2_multiplier}_N3x{n3_multiplier}')
    output_file = os.path.join(output_directory,f'{patient_id}_sleep_results_{date_today}_Wx{w_multiplier}_N2x{n2_multiplier}_N3x{n3_multiplier}.png')

    # create necessary directories if they do not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    fig.savefig(output_file)
    print(f"Results saved to {output_file}.")
