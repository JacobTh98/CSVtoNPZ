import os
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from tqdm import tqdm
from tkinter import (
    TOP,
    HORIZONTAL,
    END,
    Button,
    Label,
    Entry,
    Tk,
    Menu,
    messagebox,
    filedialog,
    Toplevel,
    ttk,
)

from src.csvConv import (
    generate_groundtruth,
    extract_el_potentials,
    re_im_re_im,
    re_re_im_im,
    plot_mesh,
)


class Title:
    def __init__(self, app) -> None:
        self.Title = Label(
            app,
            text="CSV to NPZ converter",
            font=("Arial 25 bold"),
            background="#3C5B66",
            fg="white",
        )
        self.Title.pack(ipadx=720, ipady=20, side=TOP)


class SelectingArea:
    def __init__(self, app) -> None:

        self.FirstStep = Label(app, text="1.", font=("Arial 15"), background="#FEF2B8")
        self.FirstStep.place(x=20, y=70, width=40, height=40)

        self.SelectCSV = Button(
            app,
            text="Select .csv",
            command=self.openfile,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
        )
        self.SelectCSV.place(x=80, y=70, width=200, height=40)

        self.SelectEntry = Label(
            app, text="Selected file name", font=("Arial 15"), background="#FEF2B8"
        )
        self.SelectEntry.place(x=300, y=70, width=450, height=40)

        self.SecondStep = Label(app, text="2.", font=("Arial 15"), background="#FEF2B8")
        self.SecondStep.place(x=20, y=130, width=40, height=40)

        self.SaveFolderName = Entry(app, text="", font=("Arial 15"))
        self.SaveFolderName.place(x=80, y=130, width=200, height=40)

        self.TargetFolder = Button(
            app,
            text="Create Folder",
            command=self.generate_savefolder,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
            state="disabled",
        )
        self.TargetFolder.place(x=300, y=130, width=200, height=40)

        self.ThirdStep = Label(app, text="3.", font=("Arial 15"), background="#FEF2B8")
        self.ThirdStep.place(x=20, y=190, width=40, height=40)

        self.MeshRef = Label(
            app, text="Mesh refinement", font=("Arial 15"), background="#FEF2B8"
        )
        self.MeshRef.place(x=80, y=190, width=200, height=40)
        self.h0Entry = Entry(app, font=("Arial 15"))
        self.h0Entry.place(x=300, y=190, width=90, height=40)

        self.SetMeshRef = Button(
            app,
            text="Set",
            command=self.set_mesh_ref,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
            state="disabled",
        )
        self.SetMeshRef.place(x=410, y=190, width=90, height=40)
        self.MeshPreview = Button(
            app,
            text="Preview",
            command=self.mesh_preview,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
            state="disabled",
        )
        self.MeshPreview.place(x=520, y=190, width=90, height=40)

        self.ThirdStep = Label(app, text="4.", font=("Arial 15"), background="#FEF2B8")
        self.ThirdStep.place(x=20, y=250, width=40, height=40)

        self.StartConv = Button(
            app,
            text="Convert",
            command=self.start_conv,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
            state="disabled",
        )
        self.StartConv.place(x=80, y=250, width=200, height=40)

        self.PrograssBar = ttk.Progressbar(
            app, orient=HORIZONTAL, length=300, mode="determinate"
        )
        self.PrograssBar.place(x=300, y=250, width=450, height=40)

        self.FourthStep = Label(app, text="5.", font=("Arial 15"), background="#FEF2B8")
        self.FourthStep.place(x=20, y=310, width=40, height=40)
        self.TarGzButton = Button(
            app,
            text=".tar.gz",
            command=self.tar_gz_and_delete,
            font=("Arial 15"),
            background="#D7A151",
            state="disabled",
            activebackground="#FEF2B8",
        )
        self.TarGzButton.place(x=80, y=310, width=200, height=40)

    def tar_gz_and_delete(self):
        cmd = (
            "tar cfvz "
            + str(self.SaveFolderName.get())
            + ".tar.gz "
            + str(self.SaveFolderName.get())
        )
        os.system(cmd)
        cmd = "rm -r " + str(self.SaveFolderName.get())
        os.system(cmd)

    def mesh_preview(self):

        previewWindow = Toplevel(app)
        previewWindow.title("Mesh Preview")
        previewWindow.geometry("600x600")

        image = Image.open("tmp_mesh.jpg")
        display = ImageTk.PhotoImage(image)
        label = Label(previewWindow, image=display)
        label.image = display
        label.pack()

    def set_mesh_ref(self):
        global h0
        h0 = float(self.h0Entry.get())

        def gen_mesh():
            dataframe = pd.read_csv(loadpath)
            mesh, _ = generate_groundtruth(dataframe, 0, h0=h0)
            plot_mesh(mesh, savefig=True)
            self.MeshPreview["state"] = "normal"
            self.StartConv["state"] = "normal"

        if float(h0) <= 0.01:
            result = messagebox.askquestion(
                "Are you sure you want to continue?",
                "The Meshing refinement is very high.",
                icon="warning",
            )
            if result == "yes":
                gen_mesh()
            else:
                pass

        if h0 != "" and float(h0) > 0.01:
            gen_mesh()

    def openfile(self):
        global loadpath
        loadpath = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select .csv vocabulary file.",
            filetypes=(("CSV", "*.csv"), ("all files", "*.*")),
        )
        if loadpath != "":
            print("loadpath:", loadpath)
            self.SelectEntry["text"] = loadpath.split("/")[len(loadpath.split("/")) - 1]
            self.TargetFolder["state"] = "normal"

    def generate_savefolder(self):
        global savepath
        savepath = str(self.SaveFolderName.get()) + "/"
        try:
            os.mkdir(self.SaveFolderName.get())
        except BaseException:
            print("folder already exists")
        print("savepath:", savepath)
        self.TarGzButton["state"] = "normal"
        self.SetMeshRef["state"] = "normal"

    def start_conv(self):
        try:
            os.remove("tmp_mesh.jpg")
        except BaseException:
            print("PyEITMesh preview file already deleted")
        print(loadpath)

        dataframe = pd.read_csv(loadpath)
        print("length of dataframe:", len(dataframe))
        progress_bar_step = 100 / len(dataframe)

        for N in tqdm(range(len(dataframe))):

            mesh, anomaly = generate_groundtruth(dataframe, N, h0=h0)
            complex_mat = extract_el_potentials(
                dataframe, N, delete_meas_electrodes=False
            )
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
            self.PrograssBar["value"] += progress_bar_step
            self.PrograssBar.update_idletasks()

        self.SaveFolderName.delete(0, END)
        self.TargetFolder["state"] = "disabled"
        self.PrograssBar["value"] = 0
        self.PrograssBar.update_idletasks()
        self.SelectEntry["text"] = "Selected file name"
        self.StartConv["state"] = "disabled"
        self.MeshPreview["state"] = "disabled"
        self.SetMeshRef["state"] = "disabled"
        self.h0Entry.delete(0, END)
        finish_dialog()


def info_dialog_loaded_csv(path):
    m_text = "Loaded " + str(path) + " successfully."
    messagebox.showinfo(message=m_text, title="Info")


def action_get_info_dialog():
    m_text = "\
\n\
Autor: Jacob Thönes\n\
Date: Oktober 2022\n\
Version: 1.1\n\
Contct: jacob.thoenes@uni-rostock.de \n\
"
    messagebox.showinfo(message=m_text, title="Info")


def finish_dialog():
    m_text = "Finished"
    messagebox.showinfo(message=m_text, title="Info")


"""Main Init"""
app = Tk()
app.title("CSVtoNPZ ©JaTh")
app.configure(background="#3C5B66")

dropdown = Menu(app)
datei_menu = Menu(dropdown, tearoff=0)
datei_menu.add_command(label="Exit", command=app.quit)

help_menu = Menu(dropdown, tearoff=0)
help_menu.add_command(label="Info", command=action_get_info_dialog)

dropdown.add_cascade(label="Options", menu=datei_menu)
dropdown.add_cascade(label="Help", menu=help_menu)

tf = Title(app)
sa = SelectingArea(app)


app.config(menu=dropdown)
app.geometry("770x370")
app.mainloop()
