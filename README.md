AMDA (Activity monitor data analyzer) is a small tool to analyze and plot data from [Activity monitors](https://www.phenosys.com/products/activity-monitor/). The tool is written in Python.

# Setup instructions

Used Python version is 3.8 for x64. I also recommend to use the same or a higher version. I also recommend to use the python build-in virtual environment to install all required packages. 

Now download the repository to your PC. You can use "git clone" or the above "Code"-button to download it as zip file.

1. Now we have to switch to the command line. On Windows you can use the command "cmd" or "powershell".
1. Go to the repository folder. e.g. "cd source\python\amda\"
1. Create the virtual environment with the command "py -m venv venv". The last parameter is the folder name from the previous step.
1. Now we have to activate the virtual environment. If you are using "cmd", type: "venv\Scripts\activate.bat". With "powershell" type: ".\venv\Scripts\Activate.ps1".
1. Install all packages with "pip install -r requirements.txt".
1. We need to install an extension for jupyter-lab: "jupyter labextension install @jupyter-widgets/jupyterlab-manager".
1. To activate this extension: "jupyter nbextension enable --py widgetsnbextension",
1. Now we can start JupyterLab: just type "jupyter-lab".
1. JupyterLab will now atomatically open a new web browser window.
1. Now you can open the "source/plot.ipynb" file inside of JupyterLab and analyze your data.


# Data restrictions

AMDA has some restrictions for the csv files.

1. All animals has to have valid names. Animal with "unknown" tag will irgnored.
1. All readers has to have a valid position in the csv metadata.
1. AMDA can analyze and plot the data from only one AM.

If one of the points wrong, it can be corrected with "fix_am_data.ipynb".

# How-to

It is best not to change the ".ipynb" files, but to create a copy and work in this new file. This way you always have the original file as reference.

Because AMDA creates many new files, it is recommended to create a directory for each analysis. This way all different analyses can be separated from each other.