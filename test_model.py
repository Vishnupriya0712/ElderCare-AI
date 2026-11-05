
import pickle

# Load complete ML pipeline
with open("eldercare_intent_pipeline.pkl", "rb") as file:
    model = pickle.load(file)


def predict_intent(message):

    probabilities = model.predict_proba([message])

    predicted_index = probabilities.argmax()

    intent = model.classes_[predicted_index]

    confidence = probabilities[0][predicted_index]

    return intent, confidence


# New messages not included in the training dataset
test_messages = [
    "I would love to have someone to talk to",
    "Please help me remember my daily tablets",
    "I am struggling to get proper rest",
    "Can you suggest nutritious meals",
    "I am feeling very anxious today",
    "I would like to take a gentle walk"
]

print("\n===== ELDERCARE AI - NLP TESTING =====\n")

for message in test_messages:

    intent, confidence = predict_intent(message)

    print("Message:", message)
    print("Predicted Intent:", intent)
    print("Confidence:", round(confidence * 100, 2), "%")
    print("-" * 50)
