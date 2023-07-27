# Exploring Implicit Bias in `gpt-3.5-Turbo-0613` When Generating Medical History Note Completions

We ask GPT to generate medical histories given only a patient's name, age, and gender. Does GPT give different responses if we use names more commonly used by one race vs another?

The goal is to see if there is any implicit bias shown by GPT in a medical context (shown by differing word frequencies in the returned documents). This is good to explore, as future healthcare applications that may choose to incorporate GPT models should be aware of these implicit biases.

## Generating accurate cohorts for African-American and Caucasian patients

We generate 2 cohorts of mock patients - one for mock African-American patients and one for mock Caucasian patients. Each dataset contains the mock patient's first name, last name, age, and gender. To generate the mock names, we use a [dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YL2OXB) that maps first and last names with self-reported race and ethnicity data using six U.S. Southern States voter registration data. From this dataset, we generate first-last name pairs that were likely to be found in African-American and Caucasian individuals.

However, there may be implicit gender and age biases in the voter data.

In order to generate age data for each name, we attempt to estimate a age using the AgeFromName package, which uses US Social Security Administration's Life Tables for the United States Social Security Area 1900-2100 and their baby names data to return a table probabilities of a person with a name being born in each year. We use the `get_estimated_distribution` method to probabilistically pick an age for each mock patient. In order to generate gender, we attempt to estimate gender using the first name of each mock patient using the same AgeFromName package. We probabilistically choose a gender using the packages `prob_male` and `prob_female` methods.

Neither of these approaches have yet been validated as far as I am aware.

See `cohort_generator.py` for mock patient cohort generation code. Generated cohorts can be found [here](/data/interim/cohort/).

After cohort generation, we use propensity score matching to match patients between cohorts.

We attempt to control for age and gender using propensity score matching. We don't attempt to control for other confounding variables in this mock dataset as it is difficult to do so without making large assumptions.

The final dataset contains 10,000 propensity score matched mock African-American and Caucasian patients. Matched cohort dataset can be found [here](/data/processed/cohort/).

See `propensity_score_matching.py` to see how the the final matched cohorts were generated.

## Generating the Medical History Documents From Cohort Data

See `document_generator.py` to see how I generated mock medical history documents using OpenAI and the generated cohorts. Note that generating 10,000 documents cost approx ~$10 using the gpt-3-turbo model.

The prompt attempts to have the model return the patient history as parsable JSON for easy analysis. This may influence the validity of the responses and the type of medical history returned.

All generated documents can be found [here](/data/processed/documents/).

## Analysis of Generated Documents (TODO)

Things we will explore in the generated GPT medical history documents:

- [Frequency of words used in the African-American vs Caucasian corpus](/reports/4_word_frequencies_analysis.html)
- [Uses of medications in the African-American vs Caucasian corpus](/reports/3_medication_analysis.html)
- Medical conditions found in the African-American vs Caucasian corpus

## Code Structure

```
document_generator.py - generate medical records from gpt
cohort_generator.py - generate a set of (unbalanced) mock patients using name_generator.py
name_generator.py - helper functions to generate names by race
propensity_score_matching.py - conduct propensity score matching on the generated cohorts
validate_propensity_score_matching.ipynb - validate propensity score matching worked
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

To generate a cohort and medical note documents using OpenAI:

```bash
python3 cohort_generator.py
python3 propensity_score_matching.py
python3 document_generator.py
```

To open jupyterlab:

```bash
jupyter lab
```

## References

Name data is provided by https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YL2OXB. Based on voter data
