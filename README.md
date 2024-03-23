# Computer screen specification extraction pipeline

[![CI](https://github.com/MattHag/specification-extraction/actions/workflows/build.yml/badge.svg)](https://github.com/MattHag/specification-extraction/actions/workflows/build.yml)

- Extract tables and lists from HTMLs landing pages of 30 German-speaking online shops
- Create unified, structured product specifications from the extracted data
- Evaluate the performance of three different pipeline variants
- Fine-tune a BERT model for the extraction of HDMI and DisplayPort specifications
- Print formatted product specifications to the console
- Normalize extracted data and use it for product comparison projects with filter, sort and comparison functionality

## Install dependencies
 
Then install all Python dependencies with pip.
You might want to create and enable a virtual environment first (e.g. `make virtualenv`).

```bash
$ pip install -e ."[dev]"
```

## Setup

### Initialize and fine-tune machine learning model

Download and fine-tuning of the BERT model is required to run the pipeline with the machine learning model. 
The model is fine-tuned on the gold labels from 200 computer screen on the HDMI and DisplayPort specifications.

Run the following command to download the pre-trained BERT model and fine-tune it on your local machine. 

```bash
$ python -m token_classification/train_model
```

## Usage

Run the initial setup of the pipeline with the following command.
It is also necessary, when the pipeline is run for the first time and when the data is updated.

```bash
$ python -m spec_extraction.cli
```

### Run evaluation of all three pipeline variants

The evaluation scores for all three pipeline variants can be gathered with:

```bash
$ python -m main
```


## Development

Create and enable a virtual environment (e.g. `make virtualenv`), then run the following command to installs the
development dependencies and pre-commit hooks.

```bash
$ make install
```
