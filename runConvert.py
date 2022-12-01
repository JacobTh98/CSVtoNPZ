import csv
import os

import numpy as np
import pandas as pd
from pyeit.eit.fem import PyEITMesh
from pyeit.mesh import distmesh, shape, wrapper
from tqdm import tqdm

from csvConv import *

savepath = init_save_dir()
csv_filename = init_csv_source()
    
dataframe = pd.read_csv(csv_filename)

for N in tqdm(range(len(dataframe))):

    mesh, anomaly = generate_groundtruth(dataframe,N)
    complex_mat = extract_el_potentials(dataframe,N, delete_meas_electrodes=False)
    n_el = complex_mat.shape[0]
    pot_vec = np.reshape(complex_mat,(n_el**2))
    
    np.savez(savepath + 'sample_{0:06d}.npz'.format(N), 
             mesh = mesh,
             anomaly = anomaly,
             complex_mat = complex_mat,
             pot_vec = np.reshape(complex_mat,(n_el**2)),
             pot_vec_re = pot_vec.real,
             pot_vec_im = pot_vec.imag,
             pot_vec_abs = np.abs(pot_vec),
             pot_vec_re_im_re_im = re_im_re_im(pot_vec),
             pot_vec_re_re_im_im = re_re_im_im(pot_vec),
             allow_pickle=True) 