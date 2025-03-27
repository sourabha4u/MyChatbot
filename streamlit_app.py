import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("🛒 Shopping Assistant 4.10 Chatbot")
st.write(
    "This chatbot can assist you with **order status** and **product information**. "
    "It can also greet you! Please provide your OpenAI API key to get started."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("Ask about order status, product information, or just say hi..."):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Use OpenAI to classify the intent of the user's query.
        intent_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classifier. Classify the user's query into one of the following categories: 'greeting', 'order status', 'product information', or 'other'."},
                {"role": "user", "content": prompt},
            ],
        )

        # Extract the intent from the response.
        try:
            intent = intent_response.choices[0].message.content.strip().lower()
        except (KeyError, IndexError, AttributeError):
            intent = "other"

        # Handle the intent based on the classification.
        if intent == "greeting":
            # Respond to greetings.
            with st.chat_message("assistant"):
                st.markdown("Hello! How can I assist you today? You can ask about **order status** or **product information**.")
            st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I assist you today? You can ask about **order status** or **product information**."})
        elif intent == "order status" or intent == "product information":
            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat and store it in session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Handle unsupported queries.
            with st.chat_message("assistant"):
                st.markdown(
                    "I'm sorry, I can only assist with **order status** or **product information**. "
                    "Please ask about one of these topics."
                )
            st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I can only assist with **order status** or **product information**. Please ask about one of these topics."})