"""This script generates a cohort of names for the African American and Caucasian races that is saved to the cohort folder. It does this probablistically using the probability of a name used by a person of each race. Note that the underlying dataset has some sampling bias, propensity score matching is needed before these raw cohorts can be used.
"""
import os
from collections import Counter, OrderedDict
from document_generator import print_progress_bar
from name_generator import (
    gen_black_firstname,
    gen_black_surname,
    gen_white_firstname,
    gen_white_surname,
)
from path import DATA_INTERIM_COHORT_DIR
from agefromname import AgeFromName
from dataclasses import dataclass
import numpy as np
from typing import Literal
import datetime
import json
import dataclasses
import pandas as pd
from pandas import json_normalize
from multiprocessing import cpu_count
from multiprocessing import Process
from pathlib import Path

age_from_name = AgeFromName()
BATCH_SIZE = 10
folder_location = DATA_INTERIM_COHORT_DIR


@dataclass(order=True, frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    gender: Literal["m"] | Literal["f"]

    def name(self):
        return f"{first_name.title()} {last_name}"


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def to_scalar(person):
    return {
        "first_name": person.first_name,
        "last_name": person.last_name,
        "age": person.age,
        "gender": person.gender,
    }


def gen_people(filename, get_firstname, get_surname):
    aa_people = []
    for i in range(BATCH_SIZE):
        first_name = get_firstname()
        last_name = get_surname()
        chance_male = age_from_name.prob_male(first_name)
        chance_female = age_from_name.prob_female(first_name)
        age = None
        gender = np.random.choice(["m", "f"], 1, p=[chance_male, chance_female])[0]
        needs_header = (
            not os.path.isfile(folder_location / filename)
            or os.stat(folder_location / filename).st_size == 0
        )
        # 2023 is the year the dataset was created
        age_dist = age_from_name.get_estimated_distribution(first_name, gender, 2023)
        if age_dist.any():
            today = datetime.date.today()
            # voter data, min age 18
            age_dist_df = age_dist.to_frame()
            age_dist_df = age_dist_df[age_dist_df.index <= 2005]
            age_dist_df["estimate_percentage_frac"] = (
                age_dist_df["estimate_percentage"]
                / age_dist_df["estimate_percentage"].sum()
            )
            if age_dist.any():
                try:
                    age_to_use = np.random.choice(
                        age_dist_df.index, 1, p=age_dist_df["estimate_percentage_frac"]
                    )[0]
                    if age_to_use:
                        est_age = today.year - age_to_use
                        age = est_age
                        person = Person(first_name, last_name, age, gender)
                        aa_people.append(to_scalar(person))
                except Exception as e:
                    pass
    df = pd.DataFrame(data=aa_people)
    with open(folder_location / filename, "a") as f:
        df.to_csv(
            f,
            header=needs_header,
            columns=["first_name", "last_name", "age", "gender"],
            index=False,
        )


if __name__ == "__main__":
    if not os.path.exists(folder_location):
        os.makedirs(folder_location)

    NAMES_TO_GEN = 10000
    n_cores = cpu_count()
    aa_gen_count = 0
    num_threads = 2 * n_cores
    print(f"{n_cores} cpu cores, starting {num_threads} threads")

    # run once first to generate head if needed
    gen_people("aa.csv", gen_black_firstname, gen_black_surname)
    gen_people("ca.csv", gen_white_firstname, gen_white_surname)
    aa_gen_count += BATCH_SIZE

    print_progress_bar(
        0, NAMES_TO_GEN, prefix="Progress:", suffix="Complete", length=50
    )
    while aa_gen_count <= NAMES_TO_GEN:
        a_threads = [
            Process(
                target=gen_people,
                args=("aa.csv", gen_black_firstname, gen_black_surname),
            )
            for t in range(int(num_threads / 2))
        ]
        c_threads = [
            Process(
                target=gen_people,
                args=("ca.csv", gen_white_firstname, gen_white_surname),
            )
            for t in range(int(num_threads / 2))
        ]
        threads = a_threads + c_threads

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        aa_gen_count += int(num_threads / 2) * BATCH_SIZE

        print_progress_bar(
            aa_gen_count, NAMES_TO_GEN, prefix="Progress:", suffix="Complete", length=50
        )
