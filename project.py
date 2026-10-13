import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Thailand Scope 2 GHG Dashboard", layout="wide")

# --- โหลดและเตรียมข้อมูล Pipeline ---
@st.cache_data
def load_data():
    df = pd.read_csv('dataset_electricity_usage.csv')
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'] + '-01')
    GRID_EF = 0.475  # kgCO2e/kWh
    df['Quantity_kWh'] = df['Quantity'] * 1_000_000
    df['Emissions_tCO2e'] = (df['Quantity_kWh'] * GRID_EF) / 1000
    df['Emissions_MtCO2e'] = df['Emissions_tCO2e'] / 1_000_000
    return df

df = load_data()

# --- Sidebar: ฟิลเตอร์ ---
st.sidebar.header("🔍 Filters")
years = sorted(df['Year'].unique())
selected_year = st.sidebar.selectbox("เลือกปี (Year):", years, index=len(years)-2)

# กรองข้อมูลตามปีที่เลือก
df_filtered = df[df['Year'] == selected_year]

# --- Main Dashboard ---
st.title(f"⚡ Scope 2 Electricity GHG Dashboard (ปี {selected_year})")

# 1. คำนวณ KPI Cards
total_emissions = df_filtered['Emissions_MtCO2e'].sum()

# หาเดือนที่ปล่อยสูงสุด
monthly_agg = df_filtered.groupby('Month')['Emissions_MtCO2e'].sum()
peak_month = monthly_agg.idxmax()
peak_val = monthly_agg.max()

# หา Sector ที่ปล่อยสูงสุด
sector_agg = df_filtered.groupby('Sector')['Emissions_MtCO2e'].sum()
top_sector = sector_agg.idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("การปล่อยรวมทั้งปี", f"{total_emissions:,.2f} MtCO2e")
col2.metric("เดือนที่ปล่อยสูงสุด (Peak)", f"{peak_month} ({peak_val:,.2f} MtCO2e)")
col3.metric("ภาคส่วนที่ปล่อยสูงสุด", f"{top_sector}")

st.markdown("---")

# 2. Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 สัดส่วนการปล่อยก๊าซฯ ตามภาคส่วน (Sector)")
    fig_pie = px.pie(
        df_filtered, 
        values='Emissions_MtCO2e', 
        names='Sector', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.subheader("📈 แนวโน้มการปล่อยก๊าซฯ รายเดือน")
    # เรียงลำดับเดือนตามปฏิทิน
    df_monthly = df_filtered.groupby(['Date', 'Month'])['Emissions_MtCO2e'].sum().reset_index()
    df_monthly = df_monthly.sort_values('Date')
    fig_bar = px.bar(
        df_monthly, 
        x='Month', 
        y='Emissions_MtCO2e',
        labels={'Emissions_MtCO2e': 'MtCO2e'},
        text_auto='.2f'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
