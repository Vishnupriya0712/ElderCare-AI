
import pickle
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==============================================
# ELDERCARE AI - UNSEEN NLP EVALUATION
# ==============================================

MODEL_PATH = Path(__file__).resolve().parent / "eldercare_intent_pipeline.pkl"


# ==============================================
# LOAD TRAINED MODEL
# ==============================================

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


# ==============================================
# UNSEEN TEST MESSAGES
# 3 messages for each of 12 intents
# ==============================================

test_data = [

    # Greeting
    ("Hey, good to see you", "greeting"),
    ("I hope your day is going well", "greeting"),
    ("Hello, are you available to chat", "greeting"),

    # Medicine
    ("I need to know when my next dose is due", "medicine"),
    ("Can you help me organise my prescriptions", "medicine"),
    ("I forgot whether I took my tablets this morning", "medicine"),

    # Health
    ("My knees have been hurting since yesterday", "health"),
    ("I have been coughing a lot", "health"),
    ("I am experiencing pain in my back", "health"),

    # Food
    ("What would be a good meal for lunch", "food"),
    ("I want to include more vegetables in my meals", "food"),
    ("Please give me ideas for a healthy breakfast", "food"),

    # Lonely
    ("There is nobody around to spend time with me", "lonely"),
    ("I wish I had a friend nearby", "lonely"),
    ("The house feels empty when I am alone", "lonely"),

    # Sleep
    ("I keep waking up several times during the night", "sleep"),
    ("My bedtime routine is not working", "sleep"),
    ("I struggle to fall asleep after going to bed", "sleep"),

    # Exercise
    ("I want to practise some gentle stretches", "exercise"),
    ("What physical activities can I do indoors", "exercise"),
    ("I would like to improve my walking routine", "exercise"),

    # Mental wellness
    ("I feel overwhelmed by everything lately", "mental_wellness"),
    ("My worries are making me nervous", "mental_wellness"),
    ("I have been feeling emotionally low", "mental_wellness"),

    # Family
    ("I want to arrange a video call with my son", "family"),
    ("I would love to visit my grandchildren", "family"),
    ("I miss our family get-togethers", "family"),

    # Water
    ("I keep forgetting to have enough fluids", "water"),
    ("How can I develop a regular drinking routine", "water"),
    ("I need to improve my daily hydration habits", "water"),

    # Thanks
    ("I appreciate everything you have done", "thanks"),
    ("That advice was really useful", "thanks"),
    ("I am thankful for your kindness", "thanks"),

    # Goodbye
    ("I will end our conversation here", "goodbye"),
    ("I am signing off for now", "goodbye"),
    ("Until we speak again, goodbye", "goodbye")
]


# ==============================================
# PREDICTIONS
# ==============================================

messages = [item[0] for item in test_data]
actual_labels = [item[1] for item in test_data]

predicted_labels = model.predict(messages)

probabilities = model.predict_proba(messages)


# ==============================================
# DISPLAY INDIVIDUAL RESULTS
# ==============================================

print("\n========== ELDERCARE AI NLP EVALUATION ==========\n")

correct = 0

for i, message in enumerate(messages):

    predicted = predicted_labels[i]
    actual = actual_labels[i]

    confidence = probabilities[i].max()

    result = "CORRECT" if predicted == actual else "INCORRECT"

    if predicted == actual:
        correct += 1

    print(f"Message: {message}")
    print(f"Expected Intent: {actual}")
    print(f"Predicted Intent: {predicted}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Result: {result}")
    print("-" * 55)


# ==============================================
# OVERALL ACCURACY
# ==============================================

accuracy = accuracy_score(actual_labels, predicted_labels)

print("\n========== OVERALL RESULTS ==========")

print(f"Correct Predictions: {correct}/{len(test_data)}")
print(f"Incorrect Predictions: {len(test_data) - correct}")
print(f"Accuracy: {accuracy:.2%}")


# ==============================================
# CLASSIFICATION REPORT
# ==============================================

print("\n========== CLASSIFICATION REPORT ==========\n")

print(
    classification_report(
        actual_labels,
        predicted_labels,
        labels=model.classes_,
        zero_division=0
    )
)


# ==============================================
# CONFUSION MATRIX
# ==============================================

print("\n========== CONFUSION MATRIX ==========\n")

print("Intent Labels:")
print(list(model.classes_))

print(
    confusion_matrix(
        actual_labels,
        predicted_labels,
        labels=model.classes_
    )
)

print("\n========== EVALUATION COMPLETED ==========\n")
