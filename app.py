import streamlit as st
from pdf_processing import get_pdf_text, get_text_chunks, create_vector_store, answer_question
import os
from data_visualization import visualizer

st.title("PDF Question-Answering Chatbot")

# Initialize session state for chat history, PDF processing flag, and status messages
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False  # Flag to check if the PDF has been processed
if "extraction_status" not in st.session_state:
    st.session_state.extraction_status = ""
if "chunking_status" not in st.session_state:
    st.session_state.chunking_status = ""
if "vector_store_status" not in st.session_state:
    st.session_state.vector_store_status = ""

# Sidebar for PDF upload
pdf_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")

# Process the PDF if uploaded and not processed yet
if pdf_file is not None and not st.session_state.pdf_processed:
    # Save the uploaded PDF temporarily
    with open("uploaded_pdf.pdf", "wb") as f:
        f.write(pdf_file.read())
    
    # Extract and process text from the PDF
    raw_text = get_pdf_text("uploaded_pdf.pdf")
    st.session_state.extraction_status = "PDF text extracted successfully."
    
    text_chunks = get_text_chunks(raw_text)
    st.session_state.chunking_status = "Text split into chunks successfully."
    
    create_vector_store(text_chunks)
    st.session_state.vector_store_status = "Vector store created successfully."

    # Set the PDF processed flag to True
    st.session_state.pdf_processed = True

    # Clean up the temporary file
    os.remove("uploaded_pdf.pdf")

# Display status messages in the sidebar
st.sidebar.write(st.session_state.extraction_status)
st.sidebar.write(st.session_state.chunking_status)
st.sidebar.write(st.session_state.vector_store_status)

# User question input
user_question = st.text_input("Type your question about the PDF content:")

if user_question:
    # Process the question and get the answer
    answer = answer_question(user_question)
    
    # Generate the plot and save it in the 'plots' folder
    visualizer(user_question, answer)
    
    # Update the chat history
    st.session_state.chat_history.append(("User", user_question))
    st.session_state.chat_history.append(("Bot", answer))

    # Display the chat history
    for role, message in st.session_state.chat_history:
        if role == "User":
            st.write(f"**You:** {message}")
        else:
            st.write(f"**Bot:** {message}")

    # Path to the plot image
    plot_path = os.path.join('plots', f'{user_question}.png')

    # Check if the plot image exists and display it
    if os.path.exists(plot_path):
        st.image(plot_path, caption=f"Plot for: {user_question}", use_column_width=True)
    else:
        st.write("No plot generated for this question.")

# If no PDF is uploaded
if pdf_file is None:
    st.sidebar.write("Please upload a PDF file to proceed.")
