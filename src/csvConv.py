# Impts

import os

import numpy as np

from pyeit.eit.fem import PyEITMesh
from pyeit.mesh import distmesh, shape, wrapper


try:
    import matplotlib.pyplot as plt
except BaseException:
    print(
        "To use the visualization functions:\n -plot_mesh\n -plot_cmplx_pots\n you have to import:\n import matplotlib.pyplot as plt"
    )


def plot_mesh(mesh_obj: PyEITMesh):
    """Plot PyEITMesh"""
    plt.style.use("default")
    pts = mesh_obj.node
    tri = mesh_obj.element
    x, y = pts[:, 0], pts[:, 1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.tripcolor(
        x,
        y,
        tri,
        np.real(mesh_obj.perm),
        edgecolors="k",
        shading="flat",
        alpha=0.5,
        cmap=plt.cm.viridis,
    )
    # draw electrodes
    ax.plot(x[mesh_obj.el_pos], y[mesh_obj.el_pos], "ro")
    for i, e in enumerate(mesh_obj.el_pos):
        ax.text(x[e], y[e], str(i + 1), size=12)
    ax.set_title(r"mesh")
    ax.set_aspect("equal")
    ax.set_ylim([-1.2, 1.2])
    ax.set_xlim([-1.2, 1.2])
    fig.set_size_inches(6, 6)


def plot_cmplx_pots(complex_mat):
    plt.imshow(complex_mat.real)
    plt.colorbar()
    plt.show()
    plt.imshow(complex_mat.imag)
    plt.colorbar()
    plt.show()


def init_save_dir() -> str:
    """Generate save directory."""
    sdir = input("Name of the sample directory:")

    try:
        os.mkdir(sdir)
        savepath = sdir + "/"
        print("Samples will be svaed to:", savepath)
        return savepath
    except BaseException:
        print("already exist")
        init_save_dir()


def normalize_data(data):
    """Unused"""
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def init_csv_source() -> str:
    """Initialise the .csv file."""

    csvs = [fi for fi in os.listdir() if fi.endswith(".csv")]
    if len(csvs) == 0:
        print("Please import a .csv to this directory.")
        return "empty"
    else:
        print("Select one out of these csv´s:")
        for csv in csvs:
            print(csv)
        csv_filename = input("Paste full name here:")
        return csv_filename


def julia_python_complex_convert(z: complex):
    """
    input: z = a + jb from julia: ['0.1 + 0.0im']
    returns: real, imag
    """
    return float(z.split(" ")[0]), 1j * float(z.split(" ")[-1].split("im")[0])


def generate_groundtruth(
    dataframe,
    N: int,
    el_pos: np.ndarray = np.arange(16),
    h0: float = 0.1,
    perm_abs=True,
) -> PyEITMesh:
    """
                input: one csv line
                returns: PyEITMesh

    !!! absolute or real part mesh part of the permitivity
    """
    global n_el
    dct = dataframe.loc[N]
    if perm_abs:
        # take absolute value
        real, imag = julia_python_complex_convert(dct[" perm_tank"])
        perm_tank = np.abs(complex(real, imag))
        real, imag = julia_python_complex_convert(dct[" perm_obj"])
        perm_obj = np.abs(complex(real, imag))
    else:
        # take real part
        real, _ = julia_python_complex_convert(dct[" perm_tank"])
        perm_tank = real
        real, _ = julia_python_complex_convert(dct[" perm_obj"])
        perm_obj = real

    n_el = len(el_pos)
    anomaly_props = {
        "center": [dct["x"], dct[" y"]],
        "perm": perm_obj,
        "r": dct[" r"],
    }

    # gen mesh
    pts, tri = distmesh.build(
        fd=shape.circle,
        fh=shape.area_uniform,
        pfix=shape.fix_points_circle(ppl=16),
        h0=h0,
    )

    mesh_dataset = PyEITMesh(
        node=pts,
        element=tri,
        perm=perm_tank * np.ones(tri.shape[0]),
        el_pos=el_pos,
        ref_node=0,
    )

    anom_perm = wrapper.set_perm(
        mesh_dataset, wrapper.PyEITAnomaly_Circle(**anomaly_props)
    ).perm
    mesh_dataset.perm = anom_perm
    return mesh_dataset, anomaly_props


def extract_el_potentials(dataframe, N: int, delete_meas_electrodes: bool = False):
    """
    Computes the potentials of a single row N out of a pandas dataframe.
    """
    skip_anomalie_info = 6  # DONT CHANGE

    ex_mats = list(dataframe.columns[skip_anomalie_info:])
    julia_pots = [dataframe.loc[N][ex_mats[ex]] for ex in range(len(ex_mats))]
    python_pots = [julia_python_complex_convert(pots) for pots in julia_pots]

    complex_mat = np.zeros((n_el, n_el), dtype=complex)

    idx = 0
    for i in range(n_el // 2):
        for j in range(n_el):
            complex_mat[i, j] = complex(
                python_pots[idx][0].real, python_pots[idx][1].imag
            )
            idx += 1
    idx = 0
    for i in range(n_el // 2, n_el):
        for j in range(n_el):
            complex_mat[i, j] = complex(
                -python_pots[idx][0].real, python_pots[idx][1].imag
            )
            idx += 1

    complex_mat.real = complex_mat.real / np.max(complex_mat.real)
    complex_mat.imag = complex_mat.imag / np.max(complex_mat.imag)

    if delete_meas_electrodes:
        for i in range(n_el // 2):
            zrs = complex(0, 0)
            complex_mat[i, i] = zrs
            complex_mat[i, i + 8] = zrs
        for i in range(n_el // 2, n_el):
            complex_mat[i, i] = zrs
            complex_mat[i, i - 8] = zrs

    return complex_mat


def re_im_re_im(pot_vec):
    """
    structure: [re,im,re,im,...,re,im]
    """
    new_pot_vec = np.zeros(2 * len(pot_vec))
    new_pot_vec[::2] = pot_vec.real
    new_pot_vec[1::2] = pot_vec.imag
    return new_pot_vec


def re_re_im_im(pot_vec):
    """
    structure: [re,re,re,...,im,im,im]
    """
    new_pot_vec = np.zeros(2 * len(pot_vec))
    new_pot_vec[: len(pot_vec)] = pot_vec.real
    new_pot_vec[len(pot_vec) :] = pot_vec.imag
    return new_pot_vec
