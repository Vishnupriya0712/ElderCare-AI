
import json
import pickle

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

sentences = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(pattern.lower())
        labels.append(intent["tag"])

print("\n===== ELDERCARE AI MODEL TRAINING =====")

print("Total examples:", len(sentences))
print("Total intents:", len(set(labels)))


# --------------------------------------------------
# 2. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    sentences,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# 3. CREATE TF-IDF + LOGISTIC REGRESSION PIPELINE
# --------------------------------------------------

pipeline = Pipeline([

    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),

    ("classifier", LogisticRegression(
        max_iter=2000,
        class_weight="balanced"
    ))

])


# --------------------------------------------------
# 4. TRAIN MODEL
# --------------------------------------------------

pipeline.fit(X_train, y_train)

print("\nModel training completed!")


# --------------------------------------------------
# 5. TEST MODEL
# --------------------------------------------------

predictions = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n===== TEST SET EVALUATION =====")

print("Test Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")

print(classification_report(
    y_test,
    predictions,
    zero_division=0
))


# --------------------------------------------------
# 6. CONFUSION MATRIX
# --------------------------------------------------

labels_order = sorted(set(labels))

matrix = confusion_matrix(
    y_test,
    predictions,
    labels=labels_order
)

print("\nConfusion Matrix:")
print(matrix)

print("\nIntent labels:")
print(labels_order)


# --------------------------------------------------
# 7. STRATIFIED CROSS-VALIDATION
# --------------------------------------------------

print("\n===== CROSS VALIDATION =====")

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores = cross_val_score(
    pipeline,
    sentences,
    labels,
    cv=cv,
    scoring="accuracy"
)

print("Fold scores:", scores)
print("Average CV accuracy:", round(scores.mean() * 100, 2), "%")
print("Standard deviation:", round(scores.std() * 100, 2), "%")


# --------------------------------------------------
# 8. SAVE COMPLETE PIPELINE
# --------------------------------------------------

with open("eldercare_intent_pipeline.pkl", "wb") as file:
    pickle.dump(pipeline, file)

print("\n===== MODEL SAVED =====")
print("Created: eldercare_intent_pipeline.pkl")
print("Training completed successfully!")
