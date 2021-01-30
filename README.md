# network-states
A research project centered around the analysis of distinct network states in epilepsy patients.

## get_files.py
`get_files.py` is a wrapper for two scripts: one which downloads connectivity data from ieeg.org, and another which outputs functional connectivity matrices using the raw data as an input.

### Steps for calculating functional connectivity over an interval
1. Invoke a screen: `screen -S [name]`
2. Pull the echobase image from Docker Hub: `singularity pull docker://arevell/echobase:0.0.2`
3. Start the echobase instance and name it: `singularity instance start -u --bind /gdrive/public/ [path to echobase image] [instance name]`
4. Start a shell from the instance: `singularity shell instance://[instance name]`  
5. Navigate to the script directory. On Borel, this is `cd /gdrive/public/USERS/[user folder]/network-states/util/`
6. Run the script and follow the prompts to download iEEG data and calculate functional connectivity: `python3 get_files.py`

### Steps for calculating functional connectivity over multiple intervals
`get_files.py` also allows you to calculate multiple intervals consecutively. To do this, you must supply a `.txt` file formatted in the following way for each entry:
```
[filename on iEEG.org]
[RID] (can be anything identifiable - for directory naming purposes)
[start time in us]
[end time in us]
[electrodes to ignore]
```
Here is an example of a valid `.txt` that can be used to calculate an hour of functional connectivity matrices from HUP157 and then from HUP160:
```
HUP157_phaseII
RID0365
240000000000
243600000000
EKG1,EKG2,LD1,LE10,LE11,RB10,RB11
HUP160_phaseII
RID0381
314000000000
317600000000
C3,CZ,ECG1,ECG2,F3,F7,FZ,O1,P3,PZ,RB1,RC8,RK1,T3,T5
```
If the intervals you want to calculate are from a single patient, evenly spaced, and of the same duration, then you can use `generate_spaced_intervals.py` to automatically generate a usable `.txt` file.

If the intervals you want to calculate are from a single patient, contiguous, and directly lead up to and follow each ictal period, then you can use `generate_pre_post_intervals.py`. 

Once you have a valid `.txt`, follow steps 1-5 above and then run `python3 get_files.py [path to .txt file]` to calculate all intervals consecutively.

### Troubleshooting
If an error prevents you from running `get_files.py`, you may need to install the required modules. Run the following commands in Borel and then try again:
```
cd /gdrive/public/USERS/ianzyong/ieegpy
python setup.py build
python setup.py install --user
```
