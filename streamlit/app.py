import streamlit as st
import requests

st.title("Customer Financial Summary")

uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:

    if st.button("Upload Documents"):

        files = []

        for file in uploaded_files:

            files.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        file.type
                    )
                )
            )

        response = requests.post(
            "http://127.0.0.1:8000/upload",
            files=files
        )

        if response.status_code == 200:

            st.success("Upload Successful!")

            st.json(response.json())

        else:

            st.error("Upload Failed")