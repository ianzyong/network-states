% load in data
load("data/MatlabFile.mat");

% set up array to hold processed data
num_patients = Patient(end);

% put all recordings into cell array for easy access
all_data = cell(1,3);
all_data{1} = Data_N2;
all_data{2} = Data_N3;
all_data{3} = Data_W;

% array to store stages
stages = ["N2","N3","W"];

fs = 200; % sampling rate (Hz)
seg_length = 6; % segment length (s)

%% train by channel, predictors = normalized spectral density data
% 68 percent accuracy
% array to store spectral density data
spec_dens = [];
stage_class = [];

% get fft segments from each type of data for each patient
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);

                    % perform FFT on lead data
                    fft_arr = fft(segment, n);

                    % get normalized spectral density from FFT data
                    raw_spec_dens = ((abs(fft_arr).^2)./(fs/n))';
                    spec_dens = [spec_dens;raw_spec_dens(:,1:n/2)];
                    
                    % append stage name to array
                    for row = 1:seg_sz(2)
                        stage_class = [stage_class, stages(situation)];
                    end
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(spec_dens);
training_table.stage = stage_class';

%% train by channel, predictors = top 5 peaks and amplitudes
% 61 percent accuracy
% array to store peak data
peak_data = [];
stage_class = [];

% extract spectral density peaks
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);

                    % perform FFT on lead data
                    fft_arr = fft(segment, n);

                    % get normalized spectral density from FFT data
                    raw_spec_dens = ((abs(fft_arr).^2)./(fs/n))';
                    spec_dens = raw_spec_dens(:,1:n/2);

                    % append stage name to array
                    for row = 1:seg_sz(2)
                        [pks,locs] = findpeaks(spec_dens(row,:));
                        % get top 5 peaks
                        [B,I] = maxk(pks,5);
                        peak_data = [peak_data; locs(I)*fs/n, B];
                        stage_class = [stage_class, stages(situation)];
                    end
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(peak_data);
training_table.stage = stage_class';

%% train by patient, predictors = average peak frequency and amplitude across channels
% 72.2 percent accuracy
% array to store peak data
peak_data = [];
stage_class = [];

% extract spectral density peaks
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);

                    % perform FFT on lead data
                    fft_arr = fft(segment, n);

                    % get normalized spectral density from FFT data
                    raw_spec_dens = ((abs(fft_arr).^2)./(fs/n))';
                    spec_dens = raw_spec_dens(:,1:n/2);
                    
                    all_freqs = [];
                    all_mags = [];
                    
                    for row = 1:seg_sz(2)
                        [pks,locs] = findpeaks(spec_dens(row,:));
                        [B,I] = maxk(pks,1);
                        all_freqs = [all_freqs, locs(I)*fs/n];
                        all_mags = [all_mags, B];
                    end
                    
                    % append stage name to array
                    peak_data = [peak_data; mean(all_freqs), mean(all_mags)];
                    stage_class = [stage_class, stages(situation)];
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(peak_data);
training_table.stage = stage_class';

%% train by patient, predictors = average peak frequency and amplitude and average signal variance across channels
% 83.8 percent accuracy
% array to store peak data
peak_data = [];
stage_class = [];
seg_length = 10; % segment length (s)

% extract spectral density peaks
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);

                    % perform FFT on lead data
                    fft_arr = fft(segment, n);

                    % get normalized spectral density from FFT data
                    raw_spec_dens = ((abs(fft_arr).^2)./(fs/n))';
                    spec_dens = raw_spec_dens(:,1:n/2);
                    
                    all_freqs = [];
                    all_mags = [];
                    all_vars = [];
                    
                    for row = 1:seg_sz(2)
                        [pks,locs] = findpeaks(spec_dens(row,:));
                        [B,I] = maxk(pks,1);
                        all_freqs = [all_freqs, locs(I)*fs/n];
                        all_mags = [all_mags, B];
                        all_vars = cumsum(spec_dens(row,:)*fs/n);
                    end
                    
                    % append stage name to array
                    peak_data = [peak_data; mean(all_freqs), mean(all_mags), mean(all_vars)];
                    stage_class = [stage_class, stages(situation)];
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(peak_data);
training_table.stage = stage_class';
%% train by patient, predictors = average peak frequency and amplitude and average signal variance across channels
% 6 second segment
% 72 percent accuracy
% array to store peak data
peak_data = [];
stage_class = [];
seg_length = 6; % segment length (s)

% extract spectral density peaks
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);

                    % perform FFT on lead data
                    fft_arr = fft(segment, n);

                    % get normalized spectral density from FFT data
                    raw_spec_dens = ((abs(fft_arr).^2)./(fs/n))';
                    spec_dens = raw_spec_dens(:,1:n/2);
                    
                    all_freqs = [];
                    all_mags = [];
                    all_vars = [];
                    
                    for row = 1:seg_sz(2)
                        [pks,locs] = findpeaks(spec_dens(row,:));
                        [B,I] = maxk(pks,1);
                        all_freqs = [all_freqs, locs(I)*fs/n];
                        all_mags = [all_mags, B];
                        all_vars = cumsum(spec_dens(row,:)*fs/n);
                    end
                    
                    % append stage name to array
                    peak_data = [peak_data; mean(all_freqs), mean(all_mags), mean(all_vars)];
                    stage_class = [stage_class, stages(situation)];
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(peak_data);
training_table.stage = stage_class';

%% train by patient, wavelet transform
% 6 second segment
% xxx percent accuracy
% array to store peak data
peak_data = [];
stage_class = [];
seg_length = 6; % segment length (s)

% extract spectral density peaks
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % calculate fft of each column
                    % number of points in segment data
                    n = seg_sz(1);
                    
                    all_freq_var = [];
                    all_time_var = [];
                    all_freqs = [];
                    all_mags = [];
                    
                    for row = 1:seg_sz(2)
                        % perform cwt on lead data
                        [cwt_res, f] = cwt(segment(:,row),fs);
                        abs_cwt = abs(cwt_res);
                        % append frequency and time variance to array
                        all_freq_var = [all_freq_var, var(mean(abs_cwt,2))];
                        all_time_var = [all_time_var, var(mean(abs_cwt,1))];
                        [pks,locs] = findpeaks(mean(abs_cwt,2));
                        [B,I] = maxk(pks,1);
                        all_freqs = [all_freqs, f(locs(I))];
                        all_mags = [all_mags, B];
                    end
                    
                    % take average variances
                    peak_data = [peak_data; mean(all_freq_var), mean(all_time_var), mean(all_freqs), mean(all_mags) ];
                    stage_class = [stage_class, stages(situation)];
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(peak_data);
training_table.stage = stage_class';

%% train by channel, predictors = average power and variance by frequency band
% 30 second segment split into 6-second intervals
seg_length = 30;
sub_seg_length = 6;
% 78 percent accuracy (quadratic SVM)
% arrays to store data
spec_dens = [];
stage_class = [];
band_data = [];

% get fft segments from each type of data for each patient
for situation = 1:3
    % get relevant data for the situation
    eeg_data = all_data{situation};
    for patient_id = 1:num_patients
        % get channel data corresponding to this patient
        patient_data = eeg_data(:,Patient==patient_id);
        sz = size(patient_data);
        % determine segments to take fft over
        start_ind = 1; % starting index
        if ~all(isnan(patient_data))
            while start_ind < length(patient_data)
                stop_ind = start_ind + 1;
                while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                    stop_ind = stop_ind + 1;
                end
                stop_ind = stop_ind - 1;
                segment = patient_data(start_ind:stop_ind,:);
                % only consider contiguous segments that are seg_length long
                seg_sz = size(segment);
                if seg_sz(1) == seg_length*fs
                    % for each channel
                    for chan = 1:seg_sz(2)
                        channel_data = segment(:,chan);
                        % divide into sub-segments
                        channel_segments = reshape(channel_data,sub_seg_length*fs,[]);
                        
                        % arrays to store band power
                        dp = [];
                        tp = [];
                        ap = [];
                        bp = [];
                        gp = [];
                        
                        % for each sub segment
                        for sub_seg = 1:seg_length/sub_seg_length
                            sub_seg_data = channel_segments(:,sub_seg);
                            % get spectral density of segment
                            [spec_dens, f] = pwelch(sub_seg_data,400,200,400,fs);
                            % normalize spectral density
                            int_res = cumtrapz(f,spec_dens);
                            total_area = int_res(end);
                            spec_dens = spec_dens./total_area;
                            
                            % get band power
                            int_res = cumtrapz(f(f>=0.5 & f<4),spec_dens(f>=0.5 & f<4));
                            dp = [dp, int_res(end)];
                            int_res = cumtrapz(f(f>=4 & f<8),spec_dens(f>=4 & f<8));
                            tp = [tp, int_res(end)];
                            int_res = cumtrapz(f(f>=8 & f<13),spec_dens(f>=8 & f<13));
                            ap = [ap, int_res(end)];
                            int_res = cumtrapz(f(f>=13 & f<30),spec_dens(f>=13 & f<30));
                            bp = [bp, int_res(end)];
                            int_res = cumtrapz(f(f>=30 & f<80),spec_dens(f>=30 & f<80));
                            gp = [gp, int_res(end)];
                        end
                        
                        % get average power, variance, range over
                        % subintervals
                        band_data = [band_data; mean(dp), mean(tp), mean(ap), mean(bp), mean(gp), ...
                            var(dp), var(tp), var(ap), var(bp), var(gp), ...
                            range(dp), range(tp), range(ap), range(bp), range(gp)];
                        stage_class = [stage_class, stages(situation)]; 
                    end
                end
                % reset start index
                start_ind = stop_ind + 1;
            end
        end
    end
end

% construct table for training
training_table = array2table(band_data);
training_table.stage = stage_class';
training_table = renamevars(training_table,["band_data1","band_data2","band_data3", ...
    "band_data4","band_data5","band_data6","band_data7","band_data8","band_data9", ...
    "band_data10","band_data11","band_data12","band_data13","band_data14","band_data15"], ...
    ["MeanDeltaBandPower","MeanThetaBandPower","MeanAlphaBandPower","MeanBetaBandPower","MeanGammaBandPower", ...
     "DeltaBandPowerVariance","ThetaBandPowerVariance","AlphaBandPowerVariance","BetaBandPowerVariance","GammaBandPowerVariance", ...
     "DeltaBandPowerRange","ThetaBandPowerRange","AlphaBandPowerRange","BetaBandPowerRange","GammaBandPowerRange"]);
%% save training table to xlsx
writetable(training_table,"training_table_band.xlsx")

%% Cross-validation by patient
% 5-fold cross validation
folds = 5;
num_obs = height(training_table);
all_patients = 110;

% assign each patient a random number
rand_sample = datasample(1:all_patients,all_patients,'Replace',false);
% remove patients from the sample
rand_sample(rand_sample==51 | rand_sample==86 | rand_sample==95 | rand_sample==105) = [];
num_patients = length(rand_sample);

start_inds = 1:round(num_patients/folds):num_patients;

validation_results = {};
% for each unique group
for k = 1:length(start_inds)-1
    % get validation table
    % 30 second segment split into 6-second intervals
    seg_length = 30;
    sub_seg_length = 6;

    % arrays to store data
    stage_class = [];
    band_data = [];

    % get fft segments from each type of data for each patient
    for situation = 1:3
        % get relevant data for the situation
        eeg_data = all_data{situation};
        train_sample = rand_sample;
        train_sample(ismember(rand_sample(start_inds(k):start_inds(k+1)-1),train_sample)) = [];
        for patient_id = train_sample
            % get channel data corresponding to this patient
            patient_data = eeg_data(:,Patient==patient_id);
            sz = size(patient_data);
            % determine segments to take fft over
            start_ind = 1; % starting index
            if ~all(isnan(patient_data))
                while start_ind < length(patient_data)
                    stop_ind = start_ind + 1;
                    while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                        stop_ind = stop_ind + 1;
                    end
                    stop_ind = stop_ind - 1;
                    segment = patient_data(start_ind:stop_ind,:);
                    % only consider contiguous segments that are seg_length long
                    seg_sz = size(segment);
                    if seg_sz(1) == seg_length*fs
                        % for each channel
                        for chan = 1:seg_sz(2)
                            channel_data = segment(:,chan);
                            % divide into sub-segments
                            channel_segments = reshape(channel_data,sub_seg_length*fs,[]);

                            % arrays to store band power
                            dp = [];
                            tp = [];
                            ap = [];
                            bp = [];
                            gp = [];

                            % for each sub segment
                            for sub_seg = 1:seg_length/sub_seg_length
                                sub_seg_data = channel_segments(:,sub_seg);
                                % get spectral density of segment
                                [spec_dens, f] = pwelch(sub_seg_data,400,200,400,fs);
                                % normalize spectral density
                                int_res = cumtrapz(f,spec_dens);
                                total_area = int_res(end);
                                spec_dens = spec_dens./total_area;

                                % get band power
                                int_res = cumtrapz(f(f>=0.5 & f<4),spec_dens(f>=0.5 & f<4));
                                dp = [dp, int_res(end)];
                                int_res = cumtrapz(f(f>=4 & f<8),spec_dens(f>=4 & f<8));
                                tp = [tp, int_res(end)];
                                int_res = cumtrapz(f(f>=8 & f<13),spec_dens(f>=8 & f<13));
                                ap = [ap, int_res(end)];
                                int_res = cumtrapz(f(f>=13 & f<30),spec_dens(f>=13 & f<30));
                                bp = [bp, int_res(end)];
                                int_res = cumtrapz(f(f>=30 & f<80),spec_dens(f>=30 & f<80));
                                gp = [gp, int_res(end)];
                            end

                            % get average power, variance, range over
                            % subintervals
                            band_data = [band_data; mean(dp), mean(tp), mean(ap), mean(bp), mean(gp), ...
                                var(dp), var(tp), var(ap), var(bp), var(gp), ...
                                range(dp), range(tp), range(ap), range(bp), range(gp)];
                            stage_class = [stage_class, stages(situation)]; 
                        end
                    end
                    % reset start index
                    start_ind = stop_ind + 1;
                end
            end
        end
    end
    % construct table for training
    val_table = array2table(band_data);
    val_table.stage = stage_class';
    val_table = renamevars(val_table,["band_data1","band_data2","band_data3", ...
        "band_data4","band_data5","band_data6","band_data7","band_data8","band_data9", ...
        "band_data10","band_data11","band_data12","band_data13","band_data14","band_data15"], ...
        ["MeanDeltaBandPower","MeanThetaBandPower","MeanAlphaBandPower","MeanBetaBandPower","MeanGammaBandPower", ...
         "DeltaBandPowerVariance","ThetaBandPowerVariance","AlphaBandPowerVariance","BetaBandPowerVariance","GammaBandPowerVariance", ...
         "DeltaBandPowerRange","ThetaBandPowerRange","AlphaBandPowerRange","BetaBandPowerRange","GammaBandPowerRange"]);
    
    % train classifier on the table
    [trainedClassifier, ~] = band_classifier(val_table);
    
    % arrays to store data
    stage_class = [];
    band_data = [];
    
    for situation = 1:3
        % get relevant data for the situation
        eeg_data = all_data{situation};
        for patient_id = rand_sample(start_inds(k):start_inds(k+1)-1)
            % get channel data corresponding to this patient
            patient_data = eeg_data(:,Patient==patient_id);
            sz = size(patient_data);
            % determine segments to take fft over
            start_ind = 1; % starting index
            if ~all(isnan(patient_data))
                while start_ind < length(patient_data)
                    stop_ind = start_ind + 1;
                    while stop_ind < length(patient_data) && (stop_ind < start_ind + seg_length*fs) && ~all((patient_data(stop_ind,:)) == zeros(1,sz(2)))
                        stop_ind = stop_ind + 1;
                    end
                    stop_ind = stop_ind - 1;
                    segment = patient_data(start_ind:stop_ind,:);
                    % only consider contiguous segments that are seg_length long
                    seg_sz = size(segment);
                    if seg_sz(1) == seg_length*fs
                        
                        channel_predictions = [];
                        
                        % for each channel
                        for chan = 1:seg_sz(2)
                            channel_data = segment(:,chan);
                            % divide into sub-segments
                            channel_segments = reshape(channel_data,sub_seg_length*fs,[]);

                            % arrays to store band power
                            dp = [];
                            tp = [];
                            ap = [];
                            bp = [];
                            gp = [];

                            % for each sub segment
                            for sub_seg = 1:seg_length/sub_seg_length
                                sub_seg_data = channel_segments(:,sub_seg);
                                % get spectral density of segment
                                [spec_dens, f] = pwelch(sub_seg_data,400,200,400,fs);
                                % normalize spectral density
                                int_res = cumtrapz(f,spec_dens);
                                total_area = int_res(end);
                                spec_dens = spec_dens./total_area;

                                % get band power
                                int_res = cumtrapz(f(f>=0.5 & f<4),spec_dens(f>=0.5 & f<4));
                                dp = [dp, int_res(end)];
                                int_res = cumtrapz(f(f>=4 & f<8),spec_dens(f>=4 & f<8));
                                tp = [tp, int_res(end)];
                                int_res = cumtrapz(f(f>=8 & f<13),spec_dens(f>=8 & f<13));
                                ap = [ap, int_res(end)];
                                int_res = cumtrapz(f(f>=13 & f<30),spec_dens(f>=13 & f<30));
                                bp = [bp, int_res(end)];
                                int_res = cumtrapz(f(f>=30 & f<80),spec_dens(f>=30 & f<80));
                                gp = [gp, int_res(end)];
                            end

                            % get average power, variance, range over
                            % subintervals
                            band_data = [mean(dp), mean(tp), mean(ap), mean(bp), mean(gp), ...
                                var(dp), var(tp), var(ap), var(bp), var(gp), ...
                                range(dp), range(tp), range(ap), range(bp), range(gp)];
                            band_data = array2table(band_data);
                            band_data = renamevars(band_data,["band_data1","band_data2","band_data3", ...
                            "band_data4","band_data5","band_data6","band_data7","band_data8","band_data9", ...
                            "band_data10","band_data11","band_data12","band_data13","band_data14","band_data15"], ...
                            ["MeanDeltaBandPower","MeanThetaBandPower","MeanAlphaBandPower","MeanBetaBandPower","MeanGammaBandPower", ...
                             "DeltaBandPowerVariance","ThetaBandPowerVariance","AlphaBandPowerVariance","BetaBandPowerVariance","GammaBandPowerVariance", ...
                             "DeltaBandPowerRange","ThetaBandPowerRange","AlphaBandPowerRange","BetaBandPowerRange","GammaBandPowerRange"]);
                            channel_predictions = [channel_predictions, trainedClassifier.predictFcn(band_data)];
                        end
                        validation_results(end+1,:) = {k, patient_id, char(mode(channel_predictions)), stages{situation}, 100*sum(channel_predictions == mode(channel_predictions))./length(channel_predictions), strcmp(char(mode(channel_predictions)),stages{situation})}; 
                    end
                    % reset start index
                    start_ind = stop_ind + 1;
                end
            end
        end
    end
end

val_results = cell2table(validation_results);
val_results = renamevars(val_results,["validation_results1","validation_results2","validation_results3", ...
        "validation_results4","validation_results5","validation_results6"], ...
        ["Fold","PatientID","Prediction","Actual","PercentConfidence","Correct"]);
    
% save results table to xlsx
writetable(val_results,"validation_results.xlsx")

%% validation accuracy

accuracy = 100*sum(table2array(val_results(:,6))==true)/length(table2array(val_results(:,6)));

avg_confidence_correct = mean(table2array(val_results(table2array(val_results(:,6))==true,5)));
avg_confidence_incorrect = mean(table2array(val_results(table2array(val_results(:,6))==false,5)));

% confusion matrix
C = confusionmat(table2array(val_results(:,4)),table2array(val_results(:,3)),'order',{'N3','N2','W'});
cm = confusionchart(C,["N3","N2","W"]);
cm.Title = 'Sleep Stage Classifier Using Quadratic SVM';
cm.RowSummary = 'row-normalized';
cm.ColumnSummary = 'column-normalized';
saveas(cm,"sleep_quad_svm_confusion.png")
