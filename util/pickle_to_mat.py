# TODO: work in progress

from pathlib import Path
from scipy.io import savemat

# input path to directory containing pickle files
pickle_str = input('Input path to directory containing pickle files: ')
pickle_path = Path(pickle_str)

files = os.listdir(pickle_dir)

# directory to save results
save_directory = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'notebooks',output_filename)
