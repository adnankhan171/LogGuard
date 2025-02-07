import pandas as pd
import joblib  # For saving models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


def train_and_save_models(file_path, features, target, test_size=0.2, random_state=42):
    # Load dataset
    data = pd.read_csv(file_path)

    # Encode categorical variables
    label_encoders = {}
    for col in features + [target]:
        if data[col].dtype == 'object':
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col])
            label_encoders[col] = le

    # Save label encoders
    joblib.dump(label_encoders, "label_encoders.pkl")

    # Split dataset into training and testing sets
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Standardize numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save the scaler
    joblib.dump(scaler, "scaler.pkl")

    # Initialize models
    models = {
        "Logistic Regression": LogisticRegression(random_state=random_state),
        "SVM": SVC(probability=True, random_state=random_state),
        "Random Forest": RandomForestClassifier(random_state=random_state),
     
    }

    # Train & save models
    for model_name, model in models.items():
        model.fit(X_train_scaled, y_train)
        joblib.dump(model, f"{model_name.replace(' ', '_').lower()}_model.pkl")

    print(" Models and scaler saved successfully!")

# Example usage:
file_path = "ALL_DATA.csv"  # Adjust path if needed
features = ['status', 'is_rapid_login', 'is_business_hours', 'risk_score']
target = 'result'

train_and_save_models(file_path, features, target)
