import pandas as pd


def export_to_csv():
    data = {
        "name": ["Jon Doe", "Anna Smith", "Peter Jones", "James Smith"],
        "age": [32, 34, 29, 42],
        "country": ["USA", "Canada", "UK", "USA"],
    }

    df = pd.DataFrame(data)

    df.to_csv("output.csv", index=False)
