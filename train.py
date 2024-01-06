import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
import joblib
from sklearn.metrics import recall_score
# Read the data from data.csv
data = pd.read_csv('data.csv', header=None)

# Split the data into features (X) and target variable (y)
X = data.iloc[:, 1:]
y = data.iloc[:, 0]

# Split the data into 50% training set and 50% testing set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, 'trained_model.pkl')

# Output the detailed parameters of the trained model
print("Model Coefficients:", model.coef_)
print("Model Intercept:", model.intercept_)

# Predict on the testing set
y_pred = model.predict(X_test)

# Use score method to get accuracy of model
print(accuracy_score(y_test, y_pred))
print(recall_score(y_test, y_pred))
print(recall_score(y_test, y_pred, pos_label=0))
