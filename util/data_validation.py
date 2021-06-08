# Ian Ong
# 5.23.21
# for checking whether new data may be incorporated into an existing atlas

# import modules
import sys
import os  
import os.path
import time
import numpy as np
from mef_tools.io import MefWriter, MefReader

# input parameters
mean_atlas_path = input('Path to mean connectivity .mat file: ')
std_atlas_path = input('Path to std .mat file: ')
mef_dir = input('Path to directory containing .mef files: ')

# extract data from .mef files
mef_files = os.listdir(mef_dir)

# only consider .mef files
k=0;
while k < len(mef_files):
    if mef_files[k][-4:] != ".mef":
        mef_files.pop(k)
    else:
        k = k+1

# for each .mef
for filename in mef_files:
    # read in .mef file
    filepath = os.path.join(mef_dir,filename)
    
    session_path = os.path.join(os.getcwd(),'session.mefd')
    print(session_path)

    Reader = MefReader(session_path=session_path, password2="pass")
    signals = []

    for channel in Reader.channels:
        x = Reader.get_data()
        signals.append(x)