# script to generate a text file containing calcualtion intervals for a given patient
# run the outputted text file as an argument for get_files.py
iEEG_filename = input('Input iEEG_filename: ')
rid = input('Input RID: ')
start_time_usec = int(input('Input start_time_usec: '))
stop_time_usec = int(input('Input stop_time_usec: '))
interval_spacing_usec = int(input('Input interval_spacing_usec: '))
interval_duration_usec = int(input('Input interval_duration_usec: '))
removed_channels = input('Input removed_channels: ')
filename = input('Input filename: ')

with open("{}.txt".format(filename), 'a') as txt:
    for interval_start in range(start_time_usec,stop_time_usec,interval_spacing_usec):
        txt.write('{}\n'.format(iEEG_filename))
        txt.write('{}\n'.format(rid))
        txt.write('{}\n'.format(interval_start))
        txt.write('{}\n'.format(interval_start+interval_duration_usec))
        txt.write('{}\n'.format(removed_channels))

print('File saved to {}.txt.'.format(filename))