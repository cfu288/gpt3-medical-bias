# Exploring Implicit Bias in `gpt-3.5-turbo-0613` When Generating Healthcare History Note Completions

We ask GPT to generate medical histories given only a patient's name. Does GPT give different responses if we use names more commonly used by one race vs another?

## Structure

```
document_generator.py - generate medical records from gpt
cohort_generator.py - generate a set of (unbalanced) mock patients using name_generator.py
name_generator.py - helper functions to generate names by race
propensity_score_matching.ipynb - create balanced cohorts of mock patients using propensity score matching
validate_name_gen.ipynb - notebook to see if our propensity score matching worked
word_frequency_analysis.ipynb - exploratory analysis of word frequency gpt medical records
medication_analysis.ipynb - exploratory analysis of medications found in the gpt medical records
```

## Local Development

To get started, create an `.env` file and update it with your OpenAI API key:

```bash
cp .env.example .env
```

To initialize python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To generate documents using OpenAI:

```bash
python3 main.py
```

To open jupyterlab:

```bash
jupyter lab
```

## References

Name data is provided by https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YL2OXB. Based on voter data
