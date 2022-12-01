# CSVtoNPZ

Converts a `.csv` file row-wise to `.npz` training samples and exports it into a directory.

## Run Script

To run the script just type:
`python3 runConvert.py`

Then you have to type the name of the directory the compiled `.npz` samples are saved to.
Furthermore you have to copy and paste the name e.g. *2022-11-30EIT_cyl-anom_opp-exc_discr0.2.csv* into the input field.

## Install Requirements

To install the requirements just run:
`pip install -r requirements.txt`

## CSV Structure

The Head row contains:

No. | x | y | perm_tank | perm_obj | r | ex1_pot1 | ex1_pot2 | ... | ex1_pot{n_el} | ex2_pot1 | ... | ex{n_el}_pot{n_el}
--- | --- | --- | --- |--- |--- |--- |--- |--- |--- |--- |--- |---

- {n_el} is the number of electrodes that are used during the simulation
- The ex_pot columns contain the voltage between the corresponding electrode numbers
- The provided [csv-file](2022-11-30EIT_cyl-anom_opp-exc_discr0.2.csv) has the properties:
- - The position is randomly selected in $x,y \in [-1,1]$
- - The radius is randomly selected in $r \in [0.1,1]$
- - The permittivity is komplex and also randomly choosen. The conductivities are consistent within the object area and the blank area.
- - The number of evaluated electrodes {n_el} is 16

## Contact

Email: jacob.thoenes@uni-rostock.de
