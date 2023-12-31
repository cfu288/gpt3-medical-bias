import numpy as np
import pandas as pd

from path import DATA_EXTERNAL_DIR

# Generate names by race probabilistically given dataset
# https://imai.fas.harvard.edu/research/files/names.pfn_df
# Note that this makes several assumptions (which need to be checked)
# - the probabilities of first names and sur names are independent
# - male and female names are equally represented in the data
#   - Turns out this is probably not true

fn_df = pd.read_csv(DATA_EXTERNAL_DIR / "firstnames.csv")
ln_df = pd.read_csv(DATA_EXTERNAL_DIR / "censusSurnames.csv")

fn_df["pctblack_frac"] = fn_df["pctblack"] / fn_df["pctblack"].sum()
fn_df["pctwhite_frac"] = fn_df["pctwhite"] / fn_df["pctwhite"].sum()

ln_df["pctblack_frac"] = ln_df["bla.last"] / ln_df["bla.last"].sum()
ln_df["pctwhite_frac"] = ln_df["whi.last"] / ln_df["whi.last"].sum()


def gen_black_firstname():
    return np.random.choice(fn_df["firstname"], 1, p=fn_df["pctblack_frac"])[0]


def gen_black_surname():
    return np.random.choice(ln_df["surname"], 1, p=ln_df["pctblack_frac"])[0]


def gen_black_name():
    return f"{gen_black_firstname().title()} {gen_black_surname()}"


def gen_white_firstname():
    return np.random.choice(fn_df["firstname"], 1, p=fn_df["pctwhite_frac"])[0]


def gen_white_surname():
    return np.random.choice(ln_df["surname"], 1, p=ln_df["pctwhite_frac"])[0]


def gen_white_name():
    return f"{gen_white_firstname().title()} {gen_white_surname()}"


if __name__ == "__main__":
    print(gen_black_name())
    print(gen_white_name())
