
import streamlit as st
import pandas as pd
import plotly.express as px
import glob

st.set_page_config(page_title="Spotify Lakehouse", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🎛️ Controls")
st.sidebar.markdown("Use this switch to compare Real vs. Simulated data.")

# 1. Load Data (CACHE REMOVED)
# We removed @st.cache_data so it re-reads the file every time you refresh.
def load_data():
    path = "/content/drive/MyDrive/Spotify_Lakehouse/silver/tracks.parquet"
    if not glob.glob(f"{path}/*.parquet"):
        return pd.DataFrame()
    return pd.read_parquet(path, engine='pyarrow')

df_all = load_data()

if not df_all.empty:
    # 2. THE TOGGLE SWITCH
    available_sources = df_all['data_source'].unique()
    
    # Default to 'Real' if available
    index = 0
    if "Real Spotify Data" in available_sources:
        index = list(available_sources).index("Real Spotify Data")
        
    source_selection = st.sidebar.radio(
        "Select Data Source:", 
        available_sources,
        index=index
    )

    # 3. FILTER DATA
    df = df_all[df_all['data_source'] == source_selection]
    
    # --- DASHBOARD UI ---
    st.title(f"🎧 Dashboard: {source_selection}")
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Tracks Analyzed", len(df))
    c2.metric("Unique Artists", df['artist_name'].nunique())
    top_artist = df['artist_name'].mode()[0] if not df.empty else "N/A"
    c3.metric("Top Artist", top_artist)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎤 Top Artists")
        if not df.empty:
            counts = df['artist_name'].value_counts().head(10).reset_index()
            counts.columns = ['Artist', 'Count']
            fig = px.bar(counts, x='Count', y='Artist', orientation='h', color='Count')
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("🕒 Listening Time")
        if not df.empty:
            t_counts = df['time_period'].value_counts().reset_index()
            t_counts.columns = ['Period', 'Count']
            fig2 = px.pie(t_counts, values='Count', names='Period', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📄 Raw Data")
    st.dataframe(df.head(10), use_container_width=True)

else:
    st.error("No data found. Run ETL first.")
