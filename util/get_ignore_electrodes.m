% constants to change
path_to_localization_mat = "data/patient_localization_bipolar_May25.mat";
patient_id = "HUP177";
omit_ignore = true;
omit_non_grey_matter = true;
omit_soz = true;

% code to get electrodes to ignore

struct_data = load(path_to_localization_mat);
localization_struct = struct_data.patient_localization;
patient_struct = localization_struct({localization_struct.patient}=="HUP177");

num_electrodes = length(patient_struct.labels);
ignore_binary = false(num_electrodes,1);

if omit_ignore == true
    ignore_binary = bitor(ignore_binary,patient_struct.ignore);
end

if omit_non_grey_matter == true
    ignore_binary = bitor(ignore_binary,bitor(patient_struct.gm_wm == -1, patient_struct.gm_wm == 1));
end

if omit_soz == true
    ignore_binary = bitor(ignore_binary,patient_struct.soz);
end

ignore_electrodes = join(patient_struct.labels(logical(ignore_binary)),",");
ignore_electrodes = ignore_electrodes{1}
