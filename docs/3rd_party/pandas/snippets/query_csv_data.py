import pandas as pd


def query_people_from_country(country):
    df = pd.read_csv("people.csv")

    people_from_united_states = df.query(f"Country == '{country}'")

    return people_from_united_states
