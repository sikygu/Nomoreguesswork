import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

file_path = r"C:\Users\17958\Desktop\symtrain.xlsx"
feature_columns = ['mio','B', 'COM_RAT', 'Cyclic', 'D',
            'Dc+y', 'DIT', 'DP+T', 'E', 'Inner', 'LCOM', 'Level', 'LOC', 'N',
            'NCLOC', 'NOAC', 'NOC', 'NOIC', 'OCmax', 'PDcy', 'PDpt', 'STAT',
            'TCOM_RAT', 'V', 'WMC', 'CBO', 'CLOC', 'Command', 'CONS', 'CSA', 'CSO',
            'CSOA', 'Dcy', 'DPT', 'INNER', 'jf', 'JLOC', 'Jm', 'Leve+l', 'MPC', 'n',
            'NAAC', 'NAIC', 'NOOC', 'NTP', 'OCavg', 'OPavg', 'OSavg', 'OSmax',
            'Query', 'RFC', 'TODO', "String processing", "File operations", "Network communication",
            "Database operations", "Mathematical calculation", "User Interface",
            "Business Logic", "Data Structures and Algorithms", "Systems and Tools",
            "Concurrency and Multithreading", "Exception handling",'class']
label_column = "1-suite-LLM"

def preprocess_data(df):
    print(f"Original missing values:\n{df.isnull().sum()}")
    imputer = SimpleImputer(strategy='median')
    df[feature_columns] = imputer.fit_transform(df[feature_columns])
    if df[label_column].isnull().any():
        df = df.dropna(subset=[label_column])
    print(f"Processed missing values:\n{df.isnull().sum()}")
    return df

def method_stratified():
    df = pd.read_excel(file_path)
    X, y = df[feature_columns], df[label_column]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    pd.concat([X_train, y_train], axis=1).to_excel(
        r"C:\Users\17958\Desktop\strat_train.xlsx", index=False
    )
    pd.concat([X_test, y_test], axis=1).to_excel(
        r"C:\Users\17958\Desktop\strat_test.xlsx", index=False
    )

def method_random():
    df = pd.read_excel(file_path)
    X, y = df[feature_columns], df[label_column]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    pd.concat([X_train, y_train], axis=1).to_excel(
        r"C:\Users\17958\Desktop\sym-random_train.xlsx", index=False
    )
    pd.concat([X_test, y_test], axis=1).to_excel(
        r"C:\Users\17958\Desktop\sym-random_test.xlsx", index=False
    )

def method_project_split():
    df = pd.read_excel(file_path)
    df[feature_columns] = df[feature_columns].fillna(-1)
    projects = df['metrics'].unique()
    print(f"Found {len(projects)} projects: {projects}")
    all_train = pd.DataFrame()
    all_test = pd.DataFrame()
    for project in projects:
        project_df = df[df['metrics'] == project]
        X = project_df[feature_columns]
        y = project_df[label_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)
        all_train = pd.concat([all_train, train_df])
        all_test = pd.concat([all_test, test_df])
    print(f"\nTotal training samples: {len(all_train)} | Total testing samples: {len(all_test)}")
    print(f"Original samples: {len(df)} | Merged: {len(all_train) + len(all_test)}")
    all_train.to_excel(r"C:\Users\17958\Desktop\sym-train01.xlsx", index=False)
    all_test.to_excel(r"C:\Users\17958\Desktop\sym-test01.xlsx", index=False)

if __name__ == "__main__":
    raw_df = pd.read_excel(file_path)
    print("\n Original:")
    print(f"Total samples: {len(raw_df)}")
    print(f"Category distribution:\n{raw_df[label_column].value_counts()}")
    # method_stratified()
    # method_random()
    method_project_split()
