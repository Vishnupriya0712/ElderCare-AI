
import speech_recognition as sr
import pyttsx3


# ---------------- TEXT TO SPEECH ----------------

def speak_response(text):

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as error:
        print("Voice output error:", error)


# ---------------- SPEECH TO TEXT ----------------

def listen_to_user():

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            print("Listening... Please speak.")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        print("Recognising your speech...")

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        return text

    except sr.WaitTimeoutError:
        return "No speech detected. Please try again."

    except sr.UnknownValueError:
        return "Sorry, I could not understand your speech."

    except sr.RequestError:
        return "Speech recognition service is unavailable. Please check your internet connection."

    except Exception as error:
        return f"Microphone error: {error}"
