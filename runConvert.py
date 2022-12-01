import numpy as np
import pandas as pd
from tqdm import tqdm

from src.csvConv import (
    generate_groundtruth,
    extract_el_potentials,
    init_csv_source,
    init_save_dir,
    re_im_re_im,
    re_re_im_im,
)

savepath = init_save_dir()
csv_filename = init_csv_source()

dataframe = pd.read_csv(csv_filename)

for N in tqdm(range(len(dataframe))):

    mesh, anomaly = generate_groundtruth(dataframe, N)
    complex_mat = extract_el_potentials(dataframe, N, delete_meas_electrodes=False)
    n_el = complex_mat.shape[0]
    voltage_vec = np.reshape(complex_mat, (n_el**2))

    np.savez(
        savepath + "sample_{0:06d}.npz".format(N),
        mesh=mesh,
        anomaly=anomaly,
        complex_mat=complex_mat,
        v_vec=np.reshape(complex_mat, (n_el**2)),
        v_vec_re=voltage_vec.real,
        v_vec_im=voltage_vec.imag,
        v_vec_abs=np.abs(voltage_vec),
        v_vec_re_im_re_im=re_im_re_im(voltage_vec),
        v_vec_re_re_im_im=re_re_im_im(voltage_vec),
        allow_pickle=True,
    )
