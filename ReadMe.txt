FILES AND FOLDERS DESCRIPTION
- "ReadMe.txt": File with all the instructions
- "Technical appendix.pdf": Technical appendix with missing proofs
- Excel sheet "Some datasets with small number of distinct votes.xlsx": has information on some of the datasets with small number of distinct votes.
- Folder "Performance of ordered-relax algorithm"
	- Folder "Sample datasets": has a collection of 50 sample datasets. More can be added by the user. Data is collected from "http://pabulib.org/?pfrom=4&avfrom=1.1&search=approval&orderBy=num_projects&order=desc"
	- Excel sheet "Performance of ordered-relax on sample datasets.xlsx" with results on the 50 datasets in the above folder.
	- Python code "Ordered_relax.py": code to run ordered-relax algorithm on a given PB dataset.

PACKAGES NEEDED TO RUN THE CODE
PuLP (mandatory)
GLPK solver
GUROBI solver (if possible)

CHANGING PATH IN THE CODE
In the file "Ordered_relax.py", we used relative paths. The paths of the form "./XXXX/" are to be replaced by ".\\XXXX\\" if the user is using windows instead of linux system and by "XXXX/" if the user is using macOS.

PROCEDURE TO USE THE CODE
1. Run the python file "Ordered_relax.py"
2. On being prompted, type the name of the PB dataset(filename with extension) you want to test the algorithm on. Note that this dataset must be present in "Sample datasets" folder.
	Outcome of the algorithm and the approximation ratio achieved are printed by the program.