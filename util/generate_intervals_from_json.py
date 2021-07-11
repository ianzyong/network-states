# script to generate a text file containing intervals from a .json file
# run the outputted text file as an argument for get_files.py
import json
import pandas as pd
from pathlib import Path

json_str = input('Input path to .json file: ')
json_path = Path(json_str)
xlsx_str = input('Input path to .xlsx metadata file: ')
xlsx_path = Path(xlsx_str)
max_seizures = int(input('Input max seizures per patient: '))
preictal_offset = int(input('Input preictal offset (us): '))
postictal_offset = int(input('Input postictal offset (us): '))
interictal_length = int(input('Input interictal interval length (us): '))
filename = input('Input filename for output: ')

# load json
f = open(json_path,)
data = json.load(f)

# load xlsx
df = pd.read_excel("atlas_metadata_final.xlsx")
id_dict = dict(zip(df["Patient"], df['portal_ID']))
ignore_dict = {}

# write to text file
with open("{}.txt".format(filename), 'a') as txt:
    # ICTAL INTERVALS
    # for each patient
    for patient in data["PATIENTS"]:
        seizure_count = 0
        ignore_electrodes = data["PATIENTS"][patient]["RESECTED_ELECTRODES"]
        ignore_dict[patient] = ','.join(ignore_electrodes)
        # get portal id for patient
        try:
            pid = id_dict[patient]
        except KeyError:
            print("Warning: KeyError encountered for {}, skipping...".format(patient))
            continue
            # guess the correct portal id
            # s = list(patient)
            # if s[3] == "0":
            #     del s[3]
            # pid = "".join(s) + "_phaseII"
            
        # for each ictal period
        for num in data["PATIENTS"][patient]["Events"]["Ictal"]:
            seizure_start = int(float(data["PATIENTS"][patient]["Events"]["Ictal"][num]["SeizureUEO"])*1000000)
            seizure_stop = int(float(data["PATIENTS"][patient]["Events"]["Ictal"][num]["SeizureEnd"])*1000000)
            if seizure_count < max_seizures and seizure_stop > seizure_start:
                
                # write interval to text file
                txt.write('{}\n'.format(pid))
                txt.write('{}\n'.format(patient))
                if seizure_start-preictal_offset < 0:
                    txt.write('0\n')
                else:
                    txt.write('{}\n'.format(seizure_start-preictal_offset))
                txt.write('{}\n'.format(seizure_stop+postictal_offset))
                txt.write('{}\n'.format(','.join(ignore_electrodes)))
                
                seizure_count = seizure_count + 1
    
    # INTERICTAL INTERVALS
    # for each patient
    for row in df.itertuples():
        # write interval to text file
        txt.write('{}\n'.format(row.portal_ID))
        txt.write('{}\n'.format(row.Patient))
        txt.write('{}\n'.format(row.clip1_awake*1000000))
        txt.write('{}\n'.format(row.clip1_awake*1000000+interictal_length))
        txt.write('{}\n'.format(ignore_dict[row.Patient]))

        txt.write('{}\n'.format(row.portal_ID))
        txt.write('{}\n'.format(row.Patient))
        txt.write('{}\n'.format(row.clip2_awake*1000000))
        txt.write('{}\n'.format(row.clip2_awake*1000000+interictal_length))
        txt.write('{}\n'.format(ignore_dict[row.Patient]))

print('File saved to {}.txt.'.format(filename))    
