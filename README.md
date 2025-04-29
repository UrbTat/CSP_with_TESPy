# Modeling of Thermodynamic Cycles for Concentrating Solar Power (CSP) Plants with Python



## Description

This report details the steps and provides the necessary explanations for simulating different power plant cycles using the TESpy package in Python. The simulation begins with a basic cycle, and then demonstrates how to upgrade it by incorporating other features.

## TESPy

TESPy stands for "Thermal Engineering Systems in Python" and provides a
powerful simulation toolkit for thermal engineering plants such as power
plants, district heating systems or heat pumps. It is an external extension
module within the Open Energy Modelling Framework `oemof <https://oemof.org/>`_
and can be used as a standalone package.

Examples and documentation in [TESPy](https://github.com/oemof/tespy). Find more information
about the modelling feature in the respective [online documentation](https://tespy.readthedocs.io/en/main/).

## Installing TESPy
If you have a working Python3 environment, use pypi to install the latest
tespy version:

``` bash
 pip install tespy
```

If you want to use the latest features, you might want to install the
**developer version**. See section
`Developing TESPy <http://tespy.readthedocs.io/en/dev/development/how.html>`_
for more information. The developer version is not recommended for productive
use.

## Usage

Clone the repository and build a new python environment. From the base
directory of the repository run

``` bash
pip install -r ./requirements.txt
```

to install the version requirements for the sCO2.py python script.

The original power plant specifications and results are obtained from the following
publication:
- [ ] [Andasol-2 Parabolic Trough Steam Ranking Cycle](https://doi.org/10.1016/j.jprocont.2016.01.002)
- [ ] [Supercritical CO2 Joule Cycle](https://sco2symposium.com/papers2018/cycles/052_Paper.pdf)


## Citation

The scope and functionalities of TESPy have been documented in a paper
published in the Journal of Open Source Software with an Open-Access license.
The paper is available from https://doi.org/10.21105/joss.02178.

BibTeX citation::

    @article{Witte2020,
        doi = {10.21105/joss.02178},
        year = {2020},
        publisher = {The Open Journal},
        volume = {5},
        number = {49},
        pages = {2178},
        author = {Francesco Witte and Ilja Tuschy},
        title = {{TESPy}: {T}hermal {E}ngineering {S}ystems in {P}ython},
        journal = {Journal of Open Source Software}
    }

Furthermore, a paper on the exergy analysis feature has been published in
the mdpi journal energies. You can download the pdf at
https://doi.org/10.3390/en15114087.

BibTeX citation::

    @article{Witte2022,
        doi = {10.3390/en15114087},
        year = {2022},
        volume = {15},
        number = {11},
        article-number = {4087},
        issn = {1996-1073},
        author = {Witte, Francesco and Hofmann, Mathias and Meier, Julius and Tuschy, Ilja and Tsatsaronis, George},
        title = {Generic and Open-Source Exergy Analysis&mdash;Extending the Simulation Framework TESPy},
        journal = {Energies}
    }

## Authors
- Urbano Tataranni
- Jihad Jundi
