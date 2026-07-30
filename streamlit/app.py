import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Customer Financial Summary AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Customer Financial Summary AI")
st.markdown("Upload customer financial documents to execute validation and workflow processing.")

st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("FastAPI Endpoint", value="http://127.0.0.1:8000/upload")

uploaded_files = st.file_uploader(
    "Upload Documents (PDF, PNG, JPG, JPEG, XLSX, XLS, CSV)",
    type=["pdf", "png", "jpg", "jpeg", "xlsx", "xls", "csv"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Process Documents", type="primary"):
        files_payload = []
        for file in uploaded_files:
            files_payload.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        file.type or "application/octet-stream"
                    )
                )
            )

        with st.spinner("Uploading and running workflow pipeline..."):
            try:
                response = requests.post(api_url, files=files_payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Upload and Pipeline Execution Successful!")

                    workflow_res = data.get("workflow_result", {})
                    val_res = workflow_res.get("validation_results") or {}

                    status = val_res.get("status", "N/A")
                    valid_files = val_res.get("valid_files", [])
                    invalid_files = val_res.get("invalid_files", [])

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Validation Status", status)
                    col2.metric("Valid Files", len(valid_files))
                    col3.metric("Invalid Files", len(invalid_files))

                    if valid_files:
                        st.subheader("Valid Documents")
                        df_valid = pd.DataFrame(valid_files)
                        if not df_valid.empty and "size_bytes" in df_valid.columns:
                            df_valid["size_kb"] = (df_valid["size_bytes"] / 1024).round(2)
                            display_cols = [col for col in ["file_name", "extension", "mime_type", "size_kb", "is_valid"] if col in df_valid.columns]
                            st.dataframe(df_valid[display_cols], use_container_width=True)
                        else:
                            st.dataframe(df_valid, use_container_width=True)

                    if invalid_files:
                        st.warning("⚠️ Invalid / Skipped Documents Found")
                        df_invalid = pd.DataFrame(invalid_files)
                        st.dataframe(df_invalid, use_container_width=True)

                    with st.expander("🔍 View Raw JSON Response"):
                        st.json(data)
                else:
                    st.error(f"Upload Failed (Status Code: {response.status_code})")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.write(response.text)
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Connection Error: Could not connect to FastAPI server at `{api_url}`. Please ensure FastAPI server (`uvicorn app.main:app --reload`) is running.")
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")