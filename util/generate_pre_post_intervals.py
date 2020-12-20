# script to generate a text file containing calculation intervals leading up to and after an ictal period for a given patient
# run the outputted text file as an argument for get_files.py
iEEG_filename = input('Input iEEG_filename: ')
rid = input('Input RID: ')
# start of seizure
ictal_start_time_usec = [int(x) for x in input('Input start_time_usec (seperate multiple using commas): ').split(',')]
# end of seizure
ictal_stop_time_usec = [int(x) for x in input('Input stop_time_usec (seperate multiple using commas): ').split(',')]
# duration of each interval
interval_duration_usec = int(input('Input interval_duration_usec: '))
# number of intervals each for pre- and post-ictal (e.g. inputting "4" would generate 4 intervals before and 4 intervals after the seizure)
num_intervals = int(input('Input num_intervals: '))
removed_channels = input('Input removed_channels: ')
filename = input('Input filename: ')

with open("{}.txt".format(filename), 'a') as txt:
    # for each set of seizure start/stop times
    for k in range(len(ictal_start_time_usec)):
        ictal_start = ictal_start_time_usec[k]
        ictal_stop = ictal_stop_time_usec[k]
        # write pre-ictal intervals first
        for m in range(num_intervals,0,-1):
            txt.write('{}\n'.format(iEEG_filename))
            txt.write('{}\n'.format(rid))
            txt.write('{}\n'.format(ictal_start-interval_duration_usec*m))
            txt.write('{}\n'.format(ictal_start-interval_duration_usec*(m-1)))
            txt.write('{}\n'.format(removed_channels))
        # now, write post-ictal intervals
        for m in range(num_intervals):
            txt.write('{}\n'.format(iEEG_filename))
            txt.write('{}\n'.format(rid))
            txt.write('{}\n'.format(ictal_stop+interval_duration_usec*m))
            txt.write('{}\n'.format(ictal_stop+interval_duration_usec*(m+1)))
            txt.write('{}\n'.format(removed_channels))

print('File saved to {}.txt.'.format(filename))