
import random
import re
import json
import pickle

from pathlib import Path
from functools import lru_cache


# ==================================================
# ELDERCARE AI - ML POWERED CHATBOT
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "eldercare_intent_pipeline.pkl"
REMINDERS_PATH = BASE_DIR / "reminders.json"

CONFIDENCE_THRESHOLD = 0.15


# ==================================================
# LOAD TRAINED ML MODEL
# ==================================================

@lru_cache(maxsize=1)
def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}. "
            "Please run train_model.py first."
        )

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    return model


# ==================================================
# LOAD SAVED MEDICINE REMINDERS
# ==================================================

def get_medicine_reminders():

    if not REMINDERS_PATH.exists():
        return []

    try:
        with open(REMINDERS_PATH, "r", encoding="utf-8") as file:
            reminders = json.load(file)

        return reminders if isinstance(reminders, list) else []

    except (json.JSONDecodeError, OSError) as error:
        print(f"Reminder loading error: {error}")
        return []


# ==================================================
# MEDICINE REMINDER RESPONSE
# ==================================================

def get_medicine_reminder_response():

    reminders = get_medicine_reminders()

    if not reminders:
        return (
            "You don't have any saved medicine reminders yet. "
            "You can add one in the Medicine Reminders section. 💊"
        )

    response = "Here are your saved medicine reminders:\n\n"

    for reminder in reminders:

        medicine = reminder.get("medicine", "Medicine")
        dosage = reminder.get("dosage", "Not specified")
        time = reminder.get("time", "Not specified")

        response += (
            f"💊 {medicine.title()}\n"
            f"Dosage: {dosage}\n"
            f"Time: {time}\n\n"
        )

    response += (
        "Please follow your healthcare professional's prescribed "
        "schedule. These reminders do not confirm that a dose "
        "has been taken. ❤️"
    )

    return response


# ==================================================
# CHATBOT RESPONSE DATABASE
# ==================================================

responses = {

    "greeting": [
        "Hello! 😊 How are you feeling today?",
        "Hi there! It's lovely to talk with you.",
        "Good to see you! How can I help you today?",
        "Hello! I hope you're having a wonderful day. ❤️"
    ],

    "medicine": [
        "Please follow the medicine schedule prescribed by your doctor. 💊",
        "Remember to take your medicines as prescribed. Would you like to check your reminders?",
        "I can help you keep track of your medicine schedule. Please don't change your dosage without consulting your doctor."
    ],

    "health": [
        "I'm sorry you're not feeling well. Can you tell me a little more about how you feel?",
        "Your health is important. Please consider contacting your doctor if you're feeling unwell.",
        "Please take some rest and let a family member know how you're feeling."
    ],

    "food": [
        "Eating balanced meals and drinking enough water is important. 🥗",
        "Try to include fruits, vegetables and nutritious foods in your meals.",
        "Have you had your meals today? Remember to follow any dietary advice given by your healthcare professional."
    ],

    "lonely": [
        "I'm here to keep you company. ❤️ Would you like to tell me about your day?",
        "You are not alone. Talking to family or friends can make you feel better.",
        "Would you like to share a happy memory with me?",
        "Sometimes a friendly conversation can brighten the day. I'm listening!"
    ],

    "sleep": [
        "A regular sleep schedule can help improve your sleep.",
        "Try keeping your room comfortable and avoiding caffeine close to bedtime.",
        "If you regularly have trouble sleeping, consider discussing it with your doctor."
    ],

    "exercise": [
        "Gentle physical activity, such as walking, can be beneficial when it is safe for you.",
        "Try to stay active according to your comfort and your doctor's recommendations.",
        "Remember to avoid activities that cause pain, dizziness or discomfort."
    ],

    "mental_wellness": [
        "Your feelings matter. ❤️ Would you like to talk about what's bothering you?",
        "Taking a few deep, comfortable breaths and talking to someone you trust may help.",
        "It's okay to ask for emotional support. You don't have to handle everything alone."
    ],

    "family": [
        "Spending time with family can make your day special. Have you spoken to them today?",
        "Family connections are important. Perhaps you could call someone you love.",
        "Would you like to share a favourite memory about your family?"
    ],

    "water": [
        "Remember to drink water regularly throughout the day, unless your doctor has advised you to restrict fluids.",
        "Staying hydrated is important. Keep a glass of water nearby if appropriate for you."
    ],

    "thanks": [
        "You're always welcome! 😊",
        "Happy to help you!",
        "It's my pleasure. Take care!",
        "Anytime! I'm always happy to chat."
    ],

    "goodbye": [
        "Goodbye! Take care of yourself. ❤️",
        "It was lovely talking to you. See you soon!",
        "Have a wonderful day. Stay happy and healthy!",
        "Take care! I'll be here whenever you need a chat."
    ]
}


# ==================================================
# HELPER FUNCTION
# ==================================================

def contains_keyword(message, word):

    pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"

    return re.search(pattern, message) is not None


# ==================================================
# EMERGENCY DETECTION
# ==================================================

emergency_keywords = [
    "chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "trouble breathing",
    "unconscious",
    "not responding",
    "severe bleeding",
    "stroke",
    "face drooping",
    "sudden weakness"
]


# ==================================================
# MEDICINE QUERY DETECTION
# ==================================================

medicine_queries = [
    "my medicine reminders",
    "my medicines",
    "my medicine schedule",
    "what medicines do i have",
    "what medicine do i have",
    "when should i take my medicines",
    "when should i take my medicine",
    "show my medicines",
    "show my medicine",
    "show my reminders",
    "my tablets schedule",
    "my medication schedule",
    "list my medicines",
    "list my medications"
]


def is_medicine_query(message):

    return any(query in message for query in medicine_queries)


# ==================================================
# MAIN CHATBOT FUNCTION
# ==================================================

def get_response(user_message):

    if not user_message or not user_message.strip():

        return (
            "I'm listening. Please tell me what "
            "you'd like to talk about. 😊"
        )

    message = user_message.lower().strip()

    # ----------------------------------------------
    # 1. Emergency detection
    # ----------------------------------------------

    if any(
        contains_keyword(message, word)
        for word in emergency_keywords
    ):

        return (
            "🚨 This may be a medical emergency. Please contact your "
            "local emergency services immediately. Ask someone nearby "
            "to help you and do not wait for a chatbot response. "
            "I cannot provide emergency medical care."
        )

    # ----------------------------------------------
    # 2. Saved medicine reminder lookup
    # ----------------------------------------------

    if is_medicine_query(message):

        return get_medicine_reminder_response()

    # ----------------------------------------------
    # 3. ML intent classification
    # ----------------------------------------------

    try:

        model = load_model()

        probabilities = model.predict_proba([message])[0]

        top_indices = probabilities.argsort()[-3:][::-1]

        print("\n========== INTENT ANALYSIS ==========")

        for index in top_indices:

            intent = model.classes_[index]
            confidence_score = probabilities[index]

            print(f"{intent}: {confidence_score:.2%}")

        print("=====================================\n")

        predicted_index = top_indices[0]

        predicted_intent = model.classes_[predicted_index]

        confidence = probabilities[predicted_index]

        print(f"Selected Intent: {predicted_intent}")
        print(f"Confidence: {confidence:.2%}")

        # ------------------------------------------
        # 4. Confidence-based fallback
        # ------------------------------------------

        if confidence < CONFIDENCE_THRESHOLD:

            return (
                "I'm sorry, I didn't quite understand that. 😊 "
                "Are you asking about your health, medicines, "
                "daily activities, or would you simply like to talk? ❤️"
            )

        # ------------------------------------------
        # 5. Generate chatbot response
        # ------------------------------------------

        if predicted_intent in responses:

            return random.choice(responses[predicted_intent])

        return (
            "I'm listening. Could you please tell me a little more?"
        )

    except FileNotFoundError as error:

        print(error)

        return (
            "I'm having trouble accessing my language model right now. "
            "Please try again in a moment."
        )

    except Exception as error:

        print(f"Chatbot error: {error}")

        return (
            "I'm sorry, I couldn't process that message. "
            "Could you please try again?"
        )


# ==================================================
# DIRECT TESTING
# ==================================================

if __name__ == "__main__":

    print("\n===== SAVED MEDICINE REMINDERS =====")

    reminders = get_medicine_reminders()

    if reminders:

        for reminder in reminders:

            print(
                f"Medicine: {reminder.get('medicine', 'Medicine')}\n"
                f"Dosage: {reminder.get('dosage', 'Not specified')}\n"
                f"Time: {reminder.get('time', 'Not specified')}\n"
            )

    else:

        print("No medicine reminders found.")

    print("\n===== MEDICINE CHATBOT TEST =====")

    print(get_response("What medicines do I have?"))

    print("\n===== TEST COMPLETED =====")
