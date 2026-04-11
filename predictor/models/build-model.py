import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import csv

# Function to strip whitespace from each cell in a CSV file
def strip_whitespace_from_csv(input_file, output_file):
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Strip whitespace from each cell
    stripped_rows = [[cell.strip() for cell in row] for row in rows]

    # Write stripped data to a new CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stripped_rows)

strip_whitespace_from_csv("SymptomsDiagnosis.csv", "SymptomsDiagnosis.csv")

data = pd.read_csv("SymptomsDiagnosis.csv")

label_encoder = LabelEncoder()
cols = data.columns[:-1]

train_features = data[cols]
train_labels = data[data.columns[-1]]

X_train, X_test, y_train, y_test = train_test_split(train_features, train_labels, test_size=0.25, random_state=42)

model = RandomForestClassifier(n_estimators=10)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

import joblib
joblib.dump(model, 'pred-dis.joblib')
