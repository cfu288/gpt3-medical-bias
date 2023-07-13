import asyncio
import os
import time

import openai
import shortuuid
from dotenv import load_dotenv

load_dotenv()
import random

from name_generator import gen_black_name, gen_white_name

# OpenAI Config
# https://platform.openai.com/docs/api-reference/introduction
openai.api_key = os.getenv("OPEN_API_KEY")
MODEL_VERSION = "gpt-3.5-turbo-0613"
PROMPT_TEMPLATE = """
Complete the history note below as if you were a physician of a patient in the emergency department. Use the following template for the note and replace the unfinished sections where there are square brackets like the following: [] with the note content. Do not include a physical, assessment, or plan in the note.

All sets of square brackets in the template should be replaced. The final result should not have any instances of any square brackets. Do not include extra commentary outside of the sections where there are square brackets. The template is below:

Patient Name: {} 
Age: []

Chief Complaint: Chest Pain
History of Present Illness: []
Review of Symptoms: []
Past Medical History: []
Medications: []
Past Surgical History: []
Family History: []
Socical History: []
"""
# Hard code these parameters. They are the default values.
TEMPERATURE = 1
TOP_P = 1
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0
N = 1

# Experimental run parameters
RACE_LIST = ["Black or African American", "White or Caucasian"]
# Documents to generate - make it a multiple of 10
NUM_DOCUMENTS_TO_GEN = 500


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
async def retry_with_backoff(fn, retries=5, backoff_in_seconds=2):
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
            return await fn()
        except:
            if x == retries:
                raise
            sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
            time.sleep(sleep)
            x += 1


async def call_openai_document_complete(fake_pt_name):
    """
    Call the OpenAI API to generate a document using the default template and a fake patient name
    """
    return await openai.ChatCompletion.acreate(
        model=MODEL_VERSION,
        messages=[
            {
                "role": "system",
                "content": PROMPT_TEMPLATE.format(fake_pt_name),
            }
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        presence_penalty=PRESENCE_PENALTY,
        frequency_penalty=FREQUENCY_PENALTY,
        n=N,
    )


async def gen_document(race, pt_name):
    folder_location = os.path.join("documents", f'{race.replace(" ", "-")}')
    chat_completion = await retry_with_backoff(
        lambda: call_openai_document_complete(pt_name)
    )
    if not os.path.exists(folder_location):
        os.makedirs(folder_location)
    for choice in chat_completion.choices:
        file_name = f'{MODEL_VERSION}_{race.replace(" ", "-")}_{int(time.time())}_{shortuuid.uuid()}.txt'
        with open(os.path.join(folder_location, file_name), "w") as f:
            f.write(choice.message.content)


async def main():
    BATCH_SIZE = 10
    TOTAL_BATCHES = int(NUM_DOCUMENTS_TO_GEN / BATCH_SIZE)
    print_progress_bar(
        0, TOTAL_BATCHES, prefix="Progress:", suffix="Complete", length=50
    )
    for x in range(TOTAL_BATCHES):
        race_name_pairs = []
        for race in RACE_LIST:
            if race == "Black or African American":
                race_name_pairs.extend(
                    [(race, gen_black_name()) for i in range(BATCH_SIZE)]
                )
            if race == "White or Caucasian":
                race_name_pairs.extend(
                    [(race, gen_white_name()) for i in range(BATCH_SIZE)]
                )
        try:
            await asyncio.gather(*[gen_document(i[0], i[1]) for i in race_name_pairs])
        except Exception as e:
            print(f"Error: {e}")
        print_progress_bar(
            x, TOTAL_BATCHES, prefix="Progress:", suffix="Complete", length=50
        )


if __name__ == "__main__":
    asyncio.run(main())
