

GO+ version 3.0
2020-02-10.

Denis Loustau, Christophe Moisy, Alexandre Bosc, Soisick Figuères, Simon
Martel, Virginie Moreaux, Delphine Picart-Deshors,

INRAE, UMR ISPA, Villenave d’Ornon, 33140, France.

Contact. Denis.Loustau@inrae.fr

Introduction
------------------------------------------------------
This file includes a brief description of the github and installation instructions
of the Python code. A more detailed description of the GO+ code is available
in the *\\Doc\\manual.pdf* file.

General organisation of the GO+ model code (Python 3.2).
------------------------------------------------------

All the model elements are located under the *goplus* folder. Other
folders contained the parameters files of species (\\*Parameters
files\\Species*) and site (*Parameters files\\Site)*, meteorological
data sets (\\*Met files*), or initial values of the individual tree
diameter (\\*Parameters files\\Tree stand)*. Some examples of output
files are provided in the \\*output files* folder. The \\*Scripts*
folder includes examples of the scripts that are short python codes
launching a simulation.

Three folders are located under \\*goplus*:

-   *\\goBases*

-   *\\goTools*

-   *\\goModel*

where *\\goBases* and *\\goTools* includes mathematical functions,
integration functions and definitions of elements that are used in the
main model. The third, \\*goModel*, is organising the different
component describing the biological and physical processes included in
GO+.

The GO+ model is launched using short script files. Some example
 are provided in the *Scripts* folder. These examples can be
used for simulating the data shown in Moreaux et al 2020 GMD manuscript
table 2 or figures 13 and 14 respectively.

The script file instantiates the model. It defines the list of output
variables and specifies the path of the parameters, site,
initialisation and meteorological files required by the model. The files
needed are comma separated csv files including forcing variables and
parameters as follows:

-   meteorological data set (ex. *Met\_FR-LBr\_1984-2011.csv*)

-   species-specific parameters data set (*Ppinaster.csv*,
    *Fsylvativa.csv*, *DouglasFir*.csv etc.)

-   site-specific data set *DK-Sor.csv, DE-Sol.csv etc.*

-   file including list of tree stem diameter(cm) used for initiating
    the tree stand *,* such as *FR‑Hes\_dbh\_1998* and
    *FR‑LBr\_dbh\_1987.csv*.

Installation
-------------
 GO+ runs with python3 and numpy library. To run GO+, you need to downlod and
 extract the source code (GO+ model v3.0.zip), keeping its tree directory.
 Navigate then to *Scripts* directory and run one of the program, for example :


-   Linux :

    -   install *python3* and *python3-numpy* packages

    -   from a terminal, run e.g. : *python3 Pp\_FR-LBr\_1987-2010.py*

-   Windows :

    -   install Anaconda distribution
        ([*https://www.anaconda.com/distribution/\#download-section*](https://www.anaconda.com/distribution/#download-section))

    -   from windows Start menu, select Anaconda3 and Anaconda Prompt

    -   navigate to GO+ Applications directory : cd GO+ model v3.0/Scripts

    -   enter the path of the python executable and of the goplus
        application to run, e.g. *c:\\ProgramData\\Anaconda3\\python.exe
        Pp\_FR-LBr\_1987-2010.py*


Once the program is started, you will start to see the outputs of the
model :

*1998 Age: 75.0 , nb: 328 , HEIGHT: 29.880109057009467 , DBH:
24.91856707317075 IStress: 0.0 LAI 3.0803941144628815*

Other examples are as follows. All files but the scripts are in csv
format.

  | Script (.py)             | Site parameters |  Species      |   Meteorological data      | Initial Tree Stand DBH | Output file            |
  |:-------------------------|:----------------|:--------------|:----------------- ---------|:-----------------------|:-----------------------|
  | Fs\_DK-Sor\_1998-2012    | DK-Sor          |  Fsylvatica   |   Met\_DK-Sor\_1998-2013   | DK-Sor\_dbh\_1998      | DK-Sor\_1998-2012\_d   |
  | Pp\_FR-LBr\_1987-2010    | FR-LBr          |  Ppinaster    |   Met\_FR-LBr\_1984-2011   | FR-LBr\_dbh\_1986      | FR-LBr\_1987-2011\_d   |
  | Fs\_FR-Hes\_1998-2010    | FR-Hes          |  Fsylvatica   |   Met\_FR-Hes\_1998-2010   | FR-Hes\_dbh\_1998      | FR-Hes\_1998-2010\_d   |
  | DF\_BC49\_1998-2010	     | BC-DF49         |  Douglas Fir  |   Met\_BC-DF49\_1998-2010  | generated              | BC\_DF49\_1998-2010\_d |
