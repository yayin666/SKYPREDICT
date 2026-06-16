import streamlit as st
import pandas as pd
from database.connection import SessionLocal, engine
from database.models import Base
from services.ingestion import ingest_file

st.set_page_config(page_title="Data Management", page_icon="📁", layout="wide")

st.title("📁 Data Management")
st.markdown("Upload your airline passenger dataset to clean it and load it into the SkyPredict database.")

st.info("💡 **Supported Schema:** The dataset must contain Date, Departure_City, Arrival_City, Passengers, Seat_Capacity, and Revenue_USD.")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    st.subheader("Raw Data Preview")
    try:
        if uploaded_file.name.endswith('.csv'):
            preview_df = pd.read_csv(uploaded_file, nrows=5)
        else:
            preview_df = pd.read_excel(uploaded_file, nrows=5)
        st.dataframe(preview_df)
        
        if st.button("🚀 Process and Load to Database", type="primary"):
            with st.spinner("Cleaning, aggregating, and uploading data... This may take a minute."):
                db = SessionLocal()
                try:
                    uploaded_file.seek(0)
                    success, message = ingest_file(db, uploaded_file, uploaded_file.name)
                    if success:
                        st.success(message)
                        # Clear Streamlit cache so other pages reflect new data
                        st.cache_data.clear()
                    else:
                        st.error(message)
                finally:
                    db.close()
    except Exception as e:
        st.error(f"Error reading file: {e}")

st.markdown("---")
st.subheader("⚙️ Advanced Actions")
st.warning("⚠️ **Danger Zone:** Wiping the database will permanently delete all uploaded data, forecasts, and AI recommendations.")
if st.button("🗑️ Wipe Database", type="secondary"):
    with st.spinner("Wiping database and clearing cache..."):
        try:
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            st.cache_data.clear()
            st.success("Database has been completely wiped! You may now upload a fresh dataset.")
        except Exception as e:
            st.error(f"Failed to wipe database: {e}")
