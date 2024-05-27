import pandas as pd

def inspect_csv(file_path):
    df = pd.read_csv(file_path)
    print(df.columns)
    print(df.head())

inspect_csv('datacsv.csv')