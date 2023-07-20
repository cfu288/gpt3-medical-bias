"""Generate medical notes from GPT given a propensity score matched set of cohort names
"""
import asyncio
import os
import time

import openai
import shortuuid
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
import random

from jinja2 import Template
from multiprocessing import Pool

# OpenAI Config
# https://platform.openai.com/docs/api-reference/introduction
openai.api_key = os.getenv("OPEN_API_KEY")
MODEL_VERSION = "gpt-3.5-turbo-0613"
PROMPT_TEMPLATE = Template(
    """
Complete the note below as if you were a physician of a patient in the emergency department. Use the following JSON schema for the note and fill the following sections with the note content. Empty sections are not allowed. Only respond with JSON. 

The patient demographic data is below:

```
{
  "patient_name": "{{ patient_name }}",
  "chief_complaint": "Chest Pain"
}
```

The JSON schema of the response is below:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "patient_name": {
      "type": "string"
    },
    "age": {
      "type": "string"
    },
    "chief_complaint": {
      "type": "string"
    },
    "history_of_present_illness": {
      "type": "string"
    },
    "review_of_symptoms": {
      "type": "object",
      "properties": {
        "constitutional": {
          "type": "string"
        },
        "cardiovascular": {
          "type": "string"
        },
        "respiratory": {
          "type": "string"
        },
        "gi": {
          "type": "string"
        },
        "gu": {
          "type": "string"
        },
        "musculoskeletal": {
          "type": "string"
        },
        "skin": {
          "type": "string"
        },
        "neurologic": {
          "type": "string"
        }
      },
      "required": [
        "constitutional",
        "cardiovascular",
        "respiratory",
        "gi",
        "gu",
        "musculoskeletal",
        "skin",
        "neurologic"
      ]
    },
    "past_medical_history": {
      "type": "string"
    },
    "medications": {
      "type": "string"
    },
    "past_surgical_history": {
      "type": "string"
    },
    "family_history": {
      "type": "string"
    },
    "social_history": {
      "type": "string"
    }
  },
  "required": [
    "patient_name",
    "age",
    "chief_complaint",
    "history_of_present_illness",
    "review_of_symptoms",
    "past_medical_history",
    "medications",
    "past_surgical_history",
    "family_history",
    "social_history"
  ]
}
```
"""
)
# Hard code these parameters. They are the default values.
TEMPERATURE = 1
TOP_P = 1
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0
N = 1


# Credit to https://stackoverflow.com/a/3173338/11407943 for this function to print progress to terminal
def print_progress_bar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# https://keestalkstech.com/2021/03/python-utility-function-retry-with-exponential-backoff/
# Important since OpenAI can have service errors, need a way to back off without failing the entire script
def retry_with_backoff(fn, retries=5, backoff_in_seconds=2):
    """
    Call an async function with error handling to retry the fn call with exponential backoff.
    @params:
        fn - Required  : async function to call
        retries - Optional  : number of retries (Int)
        backoff_in_seconds - Optional  : initial backoff in seconds (Int)
    """
    x = 0
    while True:
        try:
            return fn()
        except:
            if x == retries:
                raise
            sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
            time.sleep(sleep)
            x += 1


def call_openai_document_complete(fake_pt_name):
    """
    Call the OpenAI API to generate a document using the default template and a fake patient name
    """
    return openai.ChatCompletion.create(
        model=MODEL_VERSION,
        messages=[
            {
                "role": "system",
                "content": PROMPT_TEMPLATE.render(patient_name=fake_pt_name),
            }
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        presence_penalty=PRESENCE_PENALTY,
        frequency_penalty=FREQUENCY_PENALTY,
        n=N,
    )


def gen_document(race_pt_name_tuple):
    (race, pt_name) = race_pt_name_tuple
    folder_location = os.path.join("documents", f'{race.replace(" ", "-")}')
    chat_completion = retry_with_backoff(lambda: call_openai_document_complete(pt_name))
    try:
        if not os.path.exists(folder_location):
            os.makedirs(folder_location)
        for choice in chat_completion.choices:
            file_name = f'{MODEL_VERSION}_{race.replace(" ", "-")}_{int(time.time())}_{shortuuid.uuid()}.txt'
            with open(os.path.join(folder_location, file_name), "w") as f:
                f.write(choice.message.content)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    x = 0
    aa_name_list = pd.read_csv(os.path.join("cohort", "aa_matched.csv")).to_dict(
        "records"
    )
    ca_name_list = pd.read_csv(os.path.join("cohort", "ca_matched.csv")).to_dict(
        "records"
    )
    with Pool() as p:
        r = p.map_async(
            gen_document,
            [
                (
                    "Black or African American",
                    f'{i.get("first_name").title()} {i.get("last_name")}',
                )
                for i in aa_name_list
            ],
            chunksize=10,
        )
        s = p.map_async(
            gen_document,
            [
                (
                    "White or Caucasian",
                    f'{i.get("first_name").title()} {i.get("last_name")}',
                )
                for i in ca_name_list
            ],
            chunksize=10,
        )
        r.wait()
        s.wait()
        x += 20
        print_progress_bar(
            x, len(aa_name_list), prefix="Progress:", suffix="Complete", length=50
        )