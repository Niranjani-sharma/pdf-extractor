import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import LabelEncoder

# --- CONFIG ---
CSV_PATH = "data/heading_training_data_final_corrected.csv"
MODEL_PATH = "model/heading_classifier_model.pkl"
TEST_SIZE = 0.2
SEED = 42


def load_data():
    df = pd.read_csv(CSV_PATH)

    # Keep labels as-is (title, H1, H2, H3, O)
    df.dropna(subset=["text", "label"], inplace=True)

    for col in ["is_bold", "ends_colon", "all_upper"]:
        df[col] = df[col].astype(str).str.lower().map({
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0
        }).fillna(0).astype(int)

    return df


def preprocess(df):
    features = [
        "font_size", "is_bold", "y_position", "word_count", "char_count",
        "ends_colon", "all_upper"
    ]
    X = df[features]
    y_raw = df["label"]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    return X, y, label_encoder, features


def train_model(X, y):
    clf = RandomForestClassifier(n_estimators=100,
                                 max_depth=12,
                                 random_state=SEED)
    clf.fit(X, y)
    return clf


def evaluate(model, X_test, y_test, le):
    y_pred = model.predict(X_test)
    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    print(f"🎯 Macro F1 Score: {f1_score(y_test, y_pred, average='macro'):.4f}")


def save_model(model, le, features):
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump((model, le, features), MODEL_PATH)
    print(f"✅ Model saved to: {MODEL_PATH}")


def main():
    print("📥 Loading and preprocessing data...")
    df = load_data()
    X, y, le, features = preprocess(df)

    print("🔀 Splitting...")
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=TEST_SIZE,
                                                        random_state=SEED)

    print("🧠 Training classifier...")
    model = train_model(X_train, y_train)

    print("🔎 Evaluating...")
    evaluate(model, X_test, y_test, le)

    print("💾 Saving model...")
    save_model(model, le, features)


if __name__ == "__main__":
    main()
