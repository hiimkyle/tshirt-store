import streamlit as st
import time
import requests
import secrets



# Function to send data to Splunk HEC
def send_to_splunk(event_data):
    headers = {
        "Authorization": f"Splunk {secrets.splunk_hec_token}",
    }
    try:
        response = requests.post(secrets.splunk_hec_url, json=event_data, headers=headers, verify=False)
        if response.status_code != 200:
            return "error", f"Failed to send event to Splunk: {response.text}"
        else:
            return "success", "Event sent to Splunk successfully!"
    except Exception as e:
        return "error", f"Error sending event to Splunk: {e}"


# Define sizes for each row
size_rows = {
    "Me, My Friends, & AI": ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL'],
    "Ctrl + F1": ['XS', 'S', 'M', 'L', 'XL', '2XL'],
    "Commander Data": ['XS', 'S', 'M', 'L'],
    "Chasing your Tail": ['S', 'M', 'L', 'XL'],
}

# Set background image using custom CSS
background_image_url = "https://www.splunk.com/content/dam/splunk-blogs/images/en_us/2021/05/Lantern_Blog_Hero.png"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state to track selected size and timeout
if "selected_size" not in st.session_state:
    st.session_state.selected_size = {}
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# Function to handle the disappearance of the message
def handle_message_disappearance():
    if st.session_state.last_updated:
        elapsed_time = time.time() - st.session_state.last_updated
        if elapsed_time > 2:  # 2 seconds timeout
            st.session_state.last_clicked = None
            st.session_state.last_updated = None

# Loop through the rows to create titles and buttons
for title, sizes in size_rows.items():
    st.title(title)  # Display the row title

    # Create columns for the buttons in the row
    cols = st.columns(len(sizes))  # Create as many columns as there are sizes

    clicked_message = None  # Placeholder for the message to display below the row

    for col, size in zip(cols, sizes):
        with col:
            if st.button(size, key=f"{title}_{size}"):
                # Track selected size and time
                st.session_state.selected_size[title] = size
                st.session_state.last_clicked = title
                st.session_state.last_updated = time.time()

                # Prepare Splunk event data
                event_data = {
                    "event": {
                        "size": size,
                        "category": title,
                        "timestamp": time.time(),
                    },
                    "sourcetype": "_json",
                }

                # Send the event to Splunk and store the message
                status, message = send_to_splunk(event_data)
                clicked_message = (status, message)

    # Display success or error message below the row
    if clicked_message:
        status, message = clicked_message
        if status == "success":
            st.markdown(
                f"""
                <div style="
                    background-color: #d4edda;
                    color: #155724;
                    padding: 10px;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                    width: 100%;
                    text-align: center;
                    margin-top: 10px;">
                    {message}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif status == "error":
            st.markdown(
                f"""
                <div style="
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 10px;
                    border: 1px solid #f5c6cb;
                    border-radius: 5px;
                    width: 100%;
                    text-align: center;
                    margin-top: 10px;">
                    {message}
                </div>
                """,
                unsafe_allow_html=True,
            )

# Handle message disappearance
handle_message_disappearance()