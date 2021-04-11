# m00sic

Automatically generating music without data!

## Getting started

Install Magenta and create a virtual environment.

```bash
curl https://raw.githubusercontent.com/tensorflow/magenta/master/magenta/tools/magenta-install.sh > /tmp/magenta-install.sh
bash /tmp/magenta-install.sh
```

After this script is finished, **open a new terminal window** so that the environment variable changes take effect. Then, activate the newly-created virtual environment with

```bash
conda activate magenta
```

Next, install `fluidsynth` using

```bash
brew install fluidsynth
```

Then, build and install the `m00sic` package by running

```bash
python -m pip install build
python -m build
python -m pip install .
```

When developing, you should use `python -m pip install -e .` to install the package instead. For now, since we don't have an `environment.yaml` file, you need to install some dependencies manually:

```bash
python -m pip install magenta pyfluidsynth pretty_midi numba==0.48.0
```

If you'd like to run the Jupyter notebooks, you also need to install `ipykernel` and then create a new kernel specification by running

```bash
conda install -c anaconda ipykernel
python -m ipykernel install --user --name=magenta
```
