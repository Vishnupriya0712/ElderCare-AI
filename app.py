
import streamlit as st
import uuid
import re
from datetime import datetime

from chatbot import get_response
from reminders import add_reminder, load_reminders, delete_reminder, mark_as_taken
from voice_assistant import listen_to_user, speak_response
from chat_history import save_chat, load_chat_history, clear_chat_history
from daily_schedule import add_activity, load_schedule, delete_activity
from alerts import get_due_medicine_reminders, get_due_activities


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ElderCare AI",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>

/* Main background and content */

.stApp {
    background: linear-gradient(135deg, #f4fbfb 0%, #f7f8ff 100%);
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

/* Main heading */

.main-title {
    color: #234e59;
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    color: #52717a;
    font-size: 21px;
    font-weight: 600;
}

.description {
    color: #637b82;
    font-size: 16px;
}

/* Section headings */

h2, h3 {
    color: #285966 !important;
    font-weight: 700 !important;
}

/* Cards */

.care-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #dcefee;
    box-shadow: 0 4px 15px rgba(55, 115, 120, 0.07);
    margin-bottom: 15px;
}

.card-title {
    color: #285966;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.card-text {
    color: #587078;
    font-size: 16px;
}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    border-bottom: 2px solid #dcefee;
}

.stTabs [data-baseweb="tab"] {
    background-color: #eaf5f5;
    border-radius: 12px 12px 0 0;
    padding: 13px 20px;
    color: #315d67;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #ccefeb !important;
    color: #174f58 !important;
}

/* Buttons */

.stButton > button {
    background: linear-gradient(90deg, #64c9bd, #83bce9);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    min-height: 42px;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #45b5a9, #659fd5);
    color: white;
    border: none;
}

/* Input fields */

.stTextInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background-color: white;
    border: 1px solid #e1eeee;
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 12px;
}

/* Alerts */

div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* Divider */

hr {
    border-color: #dce9e9;
}

/* Labels */

label {
    color: #365b65 !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIMPLE CONVERSATIONAL CONTEXT
# --------------------------------------------------

def get_contextual_followup(previous_user_message, current_message):
    """
    Handle common follow-up messages using the previous user message.
    Return None when the ML chatbot should handle the message.
    """

    if not previous_user_message or not current_message:
        return None

    previous = previous_user_message.lower().strip()
    current = current_message.lower().strip()

    def has_term(message, terms):
        """Match whole words or exact phrases to reduce accidental matches."""
        return any(
            re.search(r"\b" + re.escape(term) + r"\b", message)
            for term in terms
        )

    # 1. Loneliness followed by a family-related message
    family_terms = [
        "child", "children", "son", "daughter",
        "grandchild", "grandchildren", "family"
    ]
    loneliness_terms = [
        "lonely", "alone", "no one", "nobody",
        "company", "someone to talk"
    ]

    if (
        has_term(previous, loneliness_terms)
        and has_term(current, family_terms)
    ):
        return (
            "It sounds like you are missing your children and family. ❤️ "
            "Would you like to call them or send them a message? "
            "I can help you think of what to say."
        )

    # 2. Anxiety or stress followed by willingness to talk
    emotional_terms = [
        "anxious", "worried", "stress", "upset",
        "overwhelmed", "nervous"
    ]
    positive_followups = [
        "yes", "yes please", "i want to talk",
        "i would like to talk", "tell you",
        "i am ready", "please listen",
        "i need to talk", "can i share"
    ]

    if (
        has_term(previous, emotional_terms)
        and (
            current in positive_followups
            or has_term(current, positive_followups[2:])
        )
    ):
        return (
            "I'm here to listen. ❤️ Take your time and tell me what has "
            "been worrying you. You can share as much or as little as you like."
        )

    # 3. Medicine discussion followed by a reminder request
    medicine_terms = [
        "medicine", "medicines",
        "tablet", "tablets",
        "pill", "pills",
        "medication", "medications"
    ]
    reminder_terms = [
        "remind", "remember", "schedule", "time"
    ]

    if (
        has_term(previous, medicine_terms)
        and has_term(current, reminder_terms)
    ):
        return (
            "I can help you check your medicine reminders. Please use the "
            "Medicine Reminders section to view or add a reminder, and follow "
            "the schedule prescribed by your healthcare professional."
        )

    return None



# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "announced_alerts" not in st.session_state:
    st.session_state.announced_alerts = set()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div style="padding: 15px 0 25px 0;">
    <div class="main-title">💙 ElderCare AI</div>
    <div class="subtitle">
        Your friendly companion for everyday elderly care
    </div>
    <div class="description" style="margin-top: 12px;">
        A simple digital companion designed to support
        senior citizens with everyday assistance.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# --------------------------------------------------
# TODAY'S ALERTS
# --------------------------------------------------

# --------------------------------------------------
# DASHBOARD OVERVIEW
# --------------------------------------------------

reminders = load_reminders()
schedule = load_schedule()
history = load_chat_history()

st.markdown("## 🌷 Your Care Dashboard")
st.write("A quick overview of your everyday care activities.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="care-card">
        <div style="font-size:35px;">💊</div>
        <div class="card-title">Medicine Reminders</div>
    </div>
    """, unsafe_allow_html=True)
    st.metric("Total reminders", len(reminders))

with col2:
    st.markdown("""
    <div class="care-card">
        <div style="font-size:35px;">🗓️</div>
        <div class="card-title">Daily Activities</div>
    </div>
    """, unsafe_allow_html=True)
    st.metric("Scheduled activities", len(schedule))

with col3:
    st.markdown("""
    <div class="care-card">
        <div style="font-size:35px;">💬</div>
        <div class="card-title">Chat History</div>
    </div>
    """, unsafe_allow_html=True)
    st.metric("Saved conversations", len(history))

st.divider()


# --------------------------------------------------
# TODAY'S ALERTS
# --------------------------------------------------


# --------------------------------------------------
# NAVIGATION TABS
# --------------------------------------------------

chat_tab, medicine_tab, history_tab, schedule_tab = st.tabs([
    "💬 Chat Assistant",
    "💊 Medicine Reminders",
    "📖 Chat History",
    "🗓️ Daily Schedule"
])


# ==================================================
# 1. CHAT ASSISTANT
# ==================================================


with chat_tab:

    st.markdown("## 💬 Your AI Companion")

    # Friendly welcome card
    st.markdown("""
    <div class="care-card">
        <div style="font-size: 35px;">🌷</div>
        <div class="card-title">Hello! Welcome to ElderCare AI</div>
        <div class="card-text">
            I'm happy to be here with you. You can talk to me
            whenever you need help with everyday activities,
            medicine reminders or a friendly conversation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    st.markdown("### ✨ What would you like to talk about?")

    suggestions = [
        "How can I stay healthy?",
        "Tell me about healthy food",
        "I am feeling lonely",
        "How can I remember my medicines?"
    ]

    suggestion_cols = st.columns(2)

    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i % 2]:
            if st.button(
                suggestion,
                key=f"suggestion_{i}",
                use_container_width=True
            ):
                st.session_state.pending_message = suggestion

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Voice and new chat buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎤 Speak to me", use_container_width=True):
            with st.spinner("Listening..."):
                try:
                    voice_text = listen_to_user()

                    if voice_text:
                        st.session_state.pending_message = voice_text
                    else:
                        st.warning("I couldn't hear you. Please try again.")

                except Exception as e:
                    st.error(f"Voice input error: {e}")

    with col2:
        if st.button("🔄 Start New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    # Process typed, suggested or voice messages
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.pending_message = user_input

    if "pending_message" in st.session_state:

        message_text = st.session_state.pending_message
        del st.session_state.pending_message

        st.session_state.messages.append({
            "role": "user",
            "content": message_text
        })

        # Find the most recent user message in this chat before adding
        # the current message. This provides short-term conversation context.
        previous_user_message = None

        for previous_message in reversed(st.session_state.messages[:-1]):
            if previous_message.get("role") == "user":
                previous_user_message = previous_message.get("content", "")
                break

        response = get_contextual_followup(
            previous_user_message,
            message_text
        )

        # If no specific follow-up rule applies, use the ML chatbot.
        if response is None:
            response = get_response(message_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        save_chat(
            st.session_state.messages,
            st.session_state.session_id
        )

        try:
            speak_response(response)
        except Exception:
            pass

        st.rerun()



# ==================================================
# 2. MEDICINE REMINDERS
# ==================================================

with medicine_tab:

    st.markdown("## 💊 Medicine Reminder Centre")

    st.write(
        "Keep track of your medicines and their scheduled times."
    )

    with st.container(border=True):

        st.markdown("### ➕ Add a New Medicine")

        with st.form("medicine_form", clear_on_submit=True):

            medicine_name = st.text_input(
                "Medicine Name",
                placeholder="Example: Vitamin D"
            )

            dosage = st.text_input(
                "Dosage",
                placeholder="Example: 1 tablet"
            )

            reminder_time = st.time_input(
                "Reminder Time"
            )

            submitted = st.form_submit_button(
                "➕ Add Reminder",
                use_container_width=True
            )

            if submitted:

                if medicine_name.strip() and dosage.strip():

                    add_reminder(
                        medicine_name,
                        dosage,
                        reminder_time.strftime("%H:%M")
                    )

                    st.success("Medicine reminder added successfully!")
                    st.rerun()

                else:
                    st.warning("Please enter the medicine name and dosage.")

    st.markdown("### 📋 Your Medicine Reminders")

    reminders = load_reminders()

    if reminders:

        for index, reminder in enumerate(reminders):

            with st.container(border=True):

                col1, col2 = st.columns([3, 2])
                taken = reminder.get("taken", False)

                with col1:
                    st.markdown(
                        f"**💊 {reminder.get('medicine', 'Medicine')}**"
                    )
                    st.write(
                        f"Dosage: {reminder.get('dosage', 'Not specified')}"
                    )
                    st.write(
                        f"⏰ Time: {reminder.get('time', 'Not specified')}"
                    )

                    if taken:
                        st.success("✅ Marked as Taken")
                    else:
                        st.warning("⏳ Not Taken Yet")

                with col2:
                    button_label = "↩️ Undo" if taken else "✅ Mark as Taken"

                    if st.button(
                        button_label,
                        key=f"taken_medicine_{index}",
                        use_container_width=True
                    ):
                        mark_as_taken(index, not taken)
                        st.rerun()

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_medicine_{index}",
                        use_container_width=True
                    ):
                        delete_reminder(index)
                        st.rerun()

    else:
        st.info("No medicine reminders added yet.")


# ==================================================
# 3. CHAT HISTORY
# ==================================================

with history_tab:

    st.markdown("## 📖 Previous Conversations")

    st.write(
        "Your saved conversations are available here."
    )

    history = load_chat_history()

    if history:

        if st.button("🗑️ Clear All Chat History"):

            clear_chat_history()
            st.success("Chat history cleared.")
            st.rerun()

        for index, session in enumerate(reversed(history)):

            with st.expander(
                f"💬 Conversation {len(history) - index} "
                f"— {session.get('date', 'Previous chat')}"
            ):

                messages = session.get("messages", [])

                for message in messages:

                    role = message.get("role", "user")
                    content = message.get("content", "")

                    if role == "assistant":
                        st.markdown(f"🤖 **ElderCare AI:** {content}")
                    else:
                        st.markdown(f"👤 **You:** {content}")

    else:
        st.info("No previous conversations found.")


# ==================================================
# 4. DAILY SCHEDULE
# ==================================================

with schedule_tab:

    st.markdown("## 🗓️ Daily Activity Planner")

    st.write(
        "Plan your daily activities and keep your day organised."
    )

    with st.container(border=True):

        st.markdown("### ➕ Add a New Activity")

        with st.form("activity_form", clear_on_submit=True):

            activity_name = st.text_input(
                "Activity Name",
                placeholder="Example: Morning Walk"
            )

            activity_date = st.date_input(
                "Activity Date"
            )

            activity_time = st.time_input(
                "Activity Time"
            )

            description = st.text_area(
                "Description",
                placeholder="Add a short description..."
            )

            submitted = st.form_submit_button(
                "➕ Add Activity",
                use_container_width=True
            )

            if submitted:

                if activity_name.strip():

                    add_activity(
                        activity_name,
                        activity_date.strftime("%Y-%m-%d"),
                        activity_time.strftime("%H:%M"),
                        description
                    )

                    st.success("Activity added successfully!")
                    st.rerun()

                else:
                    st.warning("Please enter an activity name.")

    st.markdown("### 📋 Your Daily Activities")

    schedule = load_schedule()

    if schedule:

        for index, activity in enumerate(schedule):

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(
                        f"**📌 {activity.get('activity', 'Activity')}**"
                    )

                    st.write(
                        f"📅 Date: {activity.get('date', '')}"
                    )

                    st.write(
                        f"⏰ Time: {activity.get('time', '')}"
                    )

                    st.write(
                        f"Description: "
                        f"{activity.get('description', 'No description')}"
                    )

                with col2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_activity_{index}"
                    ):
                        delete_activity(index)
                        st.rerun()

    else:
        st.info("No activities scheduled yet.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="text-align: center; padding: 15px 0;">
    <div style="font-size: 18px; color: #39747b; font-weight: 700;">
        💙 ElderCare AI
    </div>
    <div style="font-size: 13px; color: #789097; margin-top: 5px;">
        Making everyday care simpler, safer and friendlier.
    </div>
</div>
""", unsafe_allow_html=True)
