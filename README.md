# Exploring Racial Bias in `gpt-3.5-turbo-0613` - Healthcare History Note Completions

We ask GPT to generate medical histories given only a patient's name. Does GPT give different responses if we use names more commonly used by one race vs another?

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