import pandas as pd
from psmpy import PsmPy
from psmpy.plotting import *
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pickle

from path import DATA_INTERIM_COHORT_DIR, DATA_PROCESSED_COHORT_DIR
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import make_column_transformer

print("Starting propensity score matching")
COHORT_SIZE = 5000

# Create matched dataset using AA as control and CA as treatment
aa = pd.read_csv(DATA_INTERIM_COHORT_DIR / "aa.csv", nrows=COHORT_SIZE)
ca = pd.read_csv(DATA_INTERIM_COHORT_DIR / "ca.csv")
aa["race"] = 0
ca["race"] = 1
dataset = pd.concat([aa, ca])
dataset["index"] = (
    dataset.index.values.astype("str") + dataset["first_name"] + dataset["last_name"]
)

# Scale features
onehotencoder = OneHotEncoder()
standardscaler = StandardScaler()

dataset = pd.concat([aa, ca])
dataset["index"] = (
    dataset.index.values.astype("str") + dataset["first_name"] + dataset["last_name"]
)
# dataset["gender"] = onehotencoder.fit_transform(dataset[["gender"]])
dataset["age_scaled"] = standardscaler.fit_transform(dataset[["age"]])
dataset["gender_tmp"] = dataset["gender"]

transformer = make_column_transformer(
    (OneHotEncoder(), ["gender"]), remainder="passthrough"
)
transformed = transformer.fit_transform(dataset)
transformed_df = pd.DataFrame(transformed, columns=transformer.get_feature_names_out())
dataset = transformed_df.rename(
    columns={
        "remainder__first_name": "first_name",
        "remainder__last_name": "last_name",
        "remainder__age": "age",
        "remainder__race": "race",
        "remainder__index": "index",
        "remainder__age_scaled": "age_scaled",
        "remainder__gender_tmp": "gender",
    }
)
# dataset["gender"] = dataset["gender_scaled"]
dataset = dataset.astype(
    {
        "age": "int64",
        "onehotencoder__gender_f": "int32",
        "onehotencoder__gender_m": "int32",
        "age_scaled": "float64",
        "race": "int64",
    }
)

# Run matching
psm = PsmPy(
    dataset,
    treatment="race",
    exclude=["first_name", "last_name", "gender", "age"],
    indx="index",
)

# Use entire dataset to match on in non-treament group for better matching
psm.logistic_ps(balance=False)
psm.knn_matched(matcher="propensity_logit", replacement=False, caliper=None)

# Reset gender labels
# dataset["gender"] = labelencoder.inverse_transform(dataset["gender"])
dataset.drop(columns=["onehotencoder__gender_f", "onehotencoder__gender_m"])

# Filter datasets to only matched id's. Drop columns that are not needed
aa_matched_dataset = dataset[dataset["index"].isin(psm.matched_ids["index"])]
aa_matched_dataset.drop(columns=["index", "race", "age_scaled"])
ca_matched_dataset = dataset[dataset["index"].isin(psm.matched_ids["matched_ID"])]
ca_matched_dataset.drop(columns=["index", "race", "age_scaled"])

# Save matched dataset
with open(DATA_PROCESSED_COHORT_DIR / "aa_matched.csv", "w") as f:
    aa_matched_dataset.to_csv(
        f,
        header=True,
        columns=["first_name", "last_name", "age", "gender"],
        index=False,
    )

with open(DATA_PROCESSED_COHORT_DIR / "ca_matched.csv", "w") as f:
    ca_matched_dataset.to_csv(
        f,
        header=True,
        columns=["first_name", "last_name", "age", "gender"],
        index=False,
    )

# Pickle propensity score matching object
with open(DATA_PROCESSED_COHORT_DIR / "psm.pkl", "wb") as f:
    pickle.dump(psm, f)

print("Finished propensity score matching")

print(psm.matched_ids.head())
