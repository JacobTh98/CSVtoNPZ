import os
import numpy as np
import pandas as pd
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
    ttk,
)
from src.csvConv import (
    generate_groundtruth,
    extract_el_potentials,
    re_im_re_im,
    re_re_im_im,
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

        self.StartConv = Button(
            app,
            text="Convert",
            command=self.start_conv,
            font=("Arial 15"),
            background="#D7A151",
            activebackground="#FEF2B8",
            state="disabled",
        )
        self.StartConv.place(x=80, y=190, width=200, height=40)

        self.PrograssBar = ttk.Progressbar(
            app, orient=HORIZONTAL, length=300, mode="determinate"
        )
        self.PrograssBar.place(x=300, y=190, width=450, height=40)

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
        os.mkdir(self.SaveFolderName.get())
        savepath = str(self.SaveFolderName.get()) + "/"
        print("savepath:", savepath)
        self.StartConv["state"] = "normal"

    def start_conv(self):
        print(loadpath)

        dataframe = pd.read_csv(loadpath)
        progress_bar_step = 100 // len(dataframe)

        for N in range(len(dataframe)):

            mesh, anomaly = generate_groundtruth(dataframe, N)
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
        finish_dialog()


def info_dialog_loaded_csv(path):
    m_text = "Loaded " + str(path) + " successfully."
    messagebox.showinfo(message=m_text, title="Info")


def action_get_info_dialog():
    m_text = "\
\n\
Autor: Jacob Thönes\n\
Date: Oktober 2022\n\
Version: 1.0\n\
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

### top bar
dropdown = Menu(app)
datei_menu = Menu(dropdown, tearoff=0)
datei_menu.add_command(label="Exit", command=app.quit)

help_menu = Menu(dropdown, tearoff=0)
help_menu.add_command(label="Info", command=action_get_info_dialog)

dropdown.add_cascade(label="Options", menu=datei_menu)
dropdown.add_cascade(label="Help", menu=help_menu)

###
tf = Title(app)
sa = SelectingArea(app)


app.config(menu=dropdown)
app.geometry("770x250")
app.mainloop()
