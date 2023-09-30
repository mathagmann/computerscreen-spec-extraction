# Token classification

## Introduction
The token classification packages contains the code for training BERT transformer models and using them for token classification.

The following token classification tasks are supported:
- **Training (fine-tuning) a BERT model** for token classification in `train_model.py`
  - Uses our own ComputerScreens2023 dataset with labels for token classification.
- **Using a trained BERT model** for token classification (inference) in `run_model.py`

## Usage
### Training a BERT model
The `train_model.py` script can be used to train a BERT model for token classification. 

```bash
python train_model.py
```

### Run token classification with a trained BERT model
The `run_model.py` script can be used to run token classification with a trained BERT model.

```bash
python run_model.py
```
