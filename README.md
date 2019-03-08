[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/dtocean-maintenance?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/dtocean-maintenance)
[![codecov](https://codecov.io/gh/DTOcean/dtocean-maintenance/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/dtocean-maintenance)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bb34506cc82f4df883178a6e64619eaf)](https://www.codacy.com/project/H0R5E/dtocean-maintenance/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/dtocean-maintenance&amp;utm_campaign=Badge_Grade_Dashboard&amp;branchId=8410911)
[![release](https://img.shields.io/github/release/DTOcean/dtocean-maintenance.svg)](https://github.com/DTOcean/dtocean-maintenance/releases/latest)

# DTOcean Operations and Maintenance Module

The DTOcean Operations and Maintenance Module calculates costs and energy 
losses incurred from failures and maintenance of the designs created by the 
[dtocean-electrical](https://github.com/DTOcean/dtocean-electrical) and 
[dtocean-moorings](https://github.com/DTOcean/dtocean-moorings) modules and 
the OECs during their operational lifetime. It produces detailed time-based 
maintenance plans, associated costs and energy outputs. Sub-system failures are 
modelled stochastically, producing multiple alternative "histories" of the 
array lifetime, which can then be analysed statistically. 

See [dtocean-app](https://github.com/DTOcean/dtocean-app) or [dtocean-core](
https://github.com/DTOcean/dtocean-app) to use this package within the DTOcean
ecosystem.

* For python 2.7 only.

## maintenance

maintenance and development of dtocean-maintenance uses the [Anaconda 
Distribution](https://www.anaconda.com/distribution/) (Python 2.7)

### Conda Package

To install:

```
$ conda install -c dataonlygreater dtocean-maintenance
```

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
$ conda create -n _dtocean_oandm python=2.7 pip
```

Activate the environment, then copy the `.condrc` file to store maintenance  
channels:

```
$ conda activate _dtocean_oandm
$ copy .condarc %CONDA_PREFIX%
```

Install [polite](https://github.com/DTOcean/polite), [dtocean-logistics](
https://github.com/DTOcean/dtocean-logistics), [dtocean-economics](
https://github.com/DTOcean/dtocean-economics) and [dtocean-reliability](
https://github.com/DTOcean/dtocean-reliability) into the environment. For
example, if installing them from source:

```
$ cd \\path\\to\\polite
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

```
$ cd \\path\\to\\dtocean-logistics
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

```
$ cd \\path\\to\\dtocean-economics
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

```
$ cd \\path\\to\\dtocean-reliability
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

Finally, install dtocean-maintenance and its dependencies using conda and pip:

```
$ cd \\path\\to\\dtocean-maintenance
$ conda install --file requirements-conda-dev.txt
$ pip install -e .
```

To deactivate the conda environment:

```
$ conda deactivate
```

### Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

If not already active, activate the conda environment set up in the [Source 
Code](#source-code) section:

```
$ conda activate _dtocean_oandm
```

Install packages required for testing to the environment (one time only):

```
$ conda install -y pytest pytest-mock
```

Run the tests:

``` 
$ py.test tests
```

### Uninstall

To uninstall the conda package:

```
$ conda remove dtocean-maintenance
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _dtocean_oandm --all
```

## Usage

Example scripts are available in the "examples" folder of the source code.

```
cd examples
python example.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

 * Bahram Panahande at [Fraunhofer](https://www.fraunhofer.de/)
 * Mathew Topper at [TECNALIA](https://www.tecnalia.com)

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

