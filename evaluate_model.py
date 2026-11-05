
import pickle

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# 1. LOAD TRAINED MODEL
# --------------------------------------------------

with open("eldercare_intent_pipeline.pkl", "rb") as file:
    model = pickle.load(file)


# --------------------------------------------------
# 2. CREATE UNSEEN TEST DATA
# --------------------------------------------------

test_messages = [
    "Can you greet me?",
    "I would like to have a conversation",
    
    "Please remind me about my evening tablets",
    "I need to check when I take my medicine",
    
    "I have been feeling unwell since morning",
    "My body is aching today",
    
    "Suggest something nutritious for lunch",
    "What healthy snacks can I eat?",
    
    "I wish someone would sit and talk with me",
    "I feel lonely this evening",
    
    "I keep waking up in the middle of the night",
    "I am unable to get a good night's rest",
    
    "Can you recommend a simple morning walk?",
    "I want to keep myself physically active",
    
    "I am feeling anxious about things",
    "I cannot stop worrying today",
    
    "I want to arrange a call with my grandchildren",
    "I miss spending time with my daughter",
    
    "I have not been drinking enough fluids",
    "Please help me remember to stay hydrated",
    
    "I appreciate everything you have done",
    "Thank you for your suggestions",
    
    "I will talk to you another day",
    "I am leaving, goodbye"
]


# Expected intent for each test message
true_labels = [
    "greeting",
    "greeting",

    "medicine",
    "medicine",

    "health",
    "health",

    "food",
    "food",

    "lonely",
    "lonely",

    "sleep",
    "sleep",

    "exercise",
    "exercise",

    "mental_wellness",
    "mental_wellness",

    "family",
    "family",

    "water",
    "water",

    "thanks",
    "thanks",

    "goodbye",
    "goodbye"
]


# --------------------------------------------------
# 3. PREDICT INTENTS
# --------------------------------------------------

predictions = model.predict(test_messages)


# --------------------------------------------------
# 4. DISPLAY INDIVIDUAL PREDICTIONS
# --------------------------------------------------

print("\n===== ELDERCARE AI MODEL EVALUATION =====\n")

for message, actual, predicted in zip(
    test_messages,
    true_labels,
    predictions
):

    result = "CORRECT" if actual == predicted else "INCORRECT"

    print("Message:", message)
    print("Expected:", actual)
    print("Predicted:", predicted)
    print("Result:", result)
    print("-" * 50)


# --------------------------------------------------
# 5. CALCULATE ACCURACY
# --------------------------------------------------

accuracy = accuracy_score(true_labels, predictions)

print("\n===== OVERALL RESULTS =====")

print("Total test messages:", len(test_messages))

print("Correct predictions:",
      sum(a == p for a, p in zip(true_labels, predictions)))

print("Incorrect predictions:",
      sum(a != p for a, p in zip(true_labels, predictions)))

print("Test Accuracy:", round(accuracy * 100, 2), "%")


# --------------------------------------------------
# 6. CLASSIFICATION REPORT
# --------------------------------------------------

print("\n===== CLASSIFICATION REPORT =====")

print(classification_report(
    true_labels,
    predictions,
    zero_division=0
))


# --------------------------------------------------
# 7. CONFUSION MATRIX
# --------------------------------------------------

intent_labels = sorted(set(true_labels))

matrix = confusion_matrix(
    true_labels,
    predictions,
    labels=intent_labels
)

print("\n===== CONFUSION MATRIX =====")

print("Intent order:", intent_labels)

print(matrix)
