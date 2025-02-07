import pandas as pd
import joblib
from sklearn.ensemble import VotingClassifier
import numpy as np


def load_models():
    """Load trained models, scaler, and label encoders."""
    models = {
        "Logistic Regression": joblib.load("ML/logistic_regression_model.pkl"),
        "SVM": joblib.load("ML/svm_model.pkl"),
        "Random Forest": joblib.load("ML/random_forest_model.pkl"),
    }
    scaler = joblib.load("ML/scaler.pkl")
    label_encoders = joblib.load("ML/label_encoders.pkl")

    print("Models and scaler loaded successfully. Ready for offline predictions!")

    # VotingClassifier needs to be retrained, so we create it here
    voting_clf = VotingClassifier(
        estimators=[
            ("Logistic Regression", models["Logistic Regression"]),
            ("SVM", models["SVM"]),
            ("Random Forest", models["Random Forest"]),
        ],
        voting="hard"  # Use "soft" for probability-based averaging
    )

    return models, scaler, label_encoders, voting_clf


def encode_input(new_data, label_encoders):
    """Encode categorical variables in new data using label encoders."""
    new_data_encoded = new_data.copy()
    for col, le in label_encoders.items():
        if col in new_data:
            new_data_encoded[col] = le.transform([new_data[col]])[0]
    return new_data_encoded


def retrain_voting_classifier(voting_clf, models, X_train, y_train):
    """Fit the VotingClassifier using already trained base models."""
    # Extract individual model predictions to simulate training
    X_train_predictions = np.column_stack([
        models["Logistic Regression"].predict(X_train),
        models["SVM"].predict(X_train),
        models["Random Forest"].predict(X_train)
    ])

    # Fit the voting classifier
    voting_clf.fit(X_train_predictions, y_train)

    # Save the fitted VotingClassifier
    joblib.dump(voting_clf, "ML/voting_classifier.pkl")
    print("Voting classifier retrained and saved!")


def predict_danger(new_data, models, scaler, label_encoders, voting_clf):
    """Predict whether a login attempt is dangerous or not."""
    new_data_encoded = encode_input(new_data, label_encoders)
    new_data_df = pd.DataFrame([new_data_encoded])
    new_data_scaled = scaler.transform(new_data_df)

    results = {}
    print("\n🔮 Prediction Results:")
    individual_predictions = []

    for model_name, model in models.items():
        prediction = model.predict(new_data_scaled)
        result_text = prediction[0]
        results[model_name] = result_text
        print(f"{model_name} predicts: {result_text}")
        individual_predictions.append(prediction[0])  # Store predictions

    # Convert predictions to the right shape for VotingClassifier
    individual_predictions = np.array(individual_predictions).reshape(1, -1)

    # Load trained VotingClassifier
    voting_clf = joblib.load("ML/voting_classifier.pkl")
    voting_prediction = voting_clf.predict(individual_predictions)
    voting_result_text =  int(voting_prediction[0])

    results["Random Forest"] = voting_result_text
    # print(results)
    # print(f"🗳️ Voting Ensemble predicts: {voting_result_text}")
    print(voting_result_text)
    return voting_result_text


def start_model(new_login_attempt):
    models, scaler, label_encoders, voting_clf = load_models()

    output = predict_danger(new_login_attempt, models, scaler, label_encoders, voting_clf)

    return output

# if __name__ == "__main__":
#
#     models, scaler, label_encoders, voting_clf = load_models()
#
#     # Load dataset for retraining VotingClassifier
#     file_path = "vikramclean.csv"
#     data = pd.read_csv(file_path)
#     features = ['status', 'is_rapid_login', 'is_business_hours', 'risk_score']
#     target = 'result'
#
#     # Encode categorical variables
#     for col in features + [target]:
#         if data[col].dtype == 'object':
#             le = label_encoders[col]
#             data[col] = le.transform(data[col])
#
#     # Prepare training data
#     X_train = scaler.transform(data[features])  # Apply saved scaler
#     y_train = data[target]
#
#     # Retrain and save VotingClassifier
#     retrain_voting_classifier(voting_clf, models, X_train, y_train)
#
#     # Example Prediction
#     new_login_attempt = {
#         "status": 0,
#         "is_rapid_login": 1,
#         "is_business_hours": 1,
#         "risk_score": 0
#     }
#
#     output = predict_danger(new_login_attempt, models, scaler, label_encoders, voting_clf)
#
#     print(output)
