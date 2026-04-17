import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# Page Config + Theme
# -------------------------
st.set_page_config(page_title="Nassau Dashboard", layout="wide")

# Sidebar Dark Style
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #111827;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Nassau Candy Profitability Dashboard")

# -------------------------
# Load Data
# -------------------------
df = pd.read_csv("data.csv")

# -------------------------
# Data Cleaning
# -------------------------
df = df[df['Sales'] > 0]
df = df[df['Units'] > 0]

df['Units'].fillna(df['Units'].median(), inplace=True)
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')

# -------------------------
# KPI Calculation
# -------------------------
df['Gross Margin (%)'] = (df['Gross Profit'] / df['Sales']) * 100
df['Profit per Unit'] = df['Gross Profit'] / df['Units']

# -------------------------
# 🎛️ Premium Filter Panel
# -------------------------
st.sidebar.markdown("## 🎛️ Filter Panel")

st.sidebar.markdown("---")

# 📅 Date Filter
st.sidebar.markdown("### 📅 Date Selection")
date_range = st.sidebar.date_input(
    "",
    [df['Order Date'].min(), df['Order Date'].max()]
)

st.sidebar.markdown("---")

# 🏢 Division Filter
st.sidebar.markdown("### 🏢 Division")
division = st.sidebar.multiselect(
    "",
    options=df['Division'].unique(),
    default=df['Division'].unique()
)

st.sidebar.markdown("---")

# 📦 Product Filter (SMART)
st.sidebar.markdown("### 📦 Product")

filtered_products = df[df['Division'].isin(division)]['Product Name'].unique()

product = st.sidebar.multiselect(
    "",
    options=filtered_products,
    default=filtered_products
)

st.sidebar.markdown("---")

# 📊 Margin Filter
st.sidebar.markdown("### 📊 Margin Range (%)")
margin_range = st.sidebar.slider(
    "",
    int(df['Gross Margin (%)'].min()),
    int(df['Gross Margin (%)'].max()),
    (0, 100)
)

st.sidebar.markdown("---")

# 💰 Profit Filter
st.sidebar.markdown("### 💰 Profit Range")
profit_range = st.sidebar.slider(
    "",
    int(df['Gross Profit'].min()),
    int(df['Gross Profit'].max()),
    (int(df['Gross Profit'].min()), int(df['Gross Profit'].max()))
)

st.sidebar.markdown("---")

# -------------------------
# Apply Filters
# -------------------------
df = df[(df['Order Date'] >= pd.to_datetime(date_range[0])) &
        (df['Order Date'] <= pd.to_datetime(date_range[1]))]

df = df[df['Division'].isin(division)]

df = df[df['Product Name'].isin(product)]

df = df[(df['Gross Margin (%)'] >= margin_range[0]) &
        (df['Gross Margin (%)'] <= margin_range[1])]

df = df[(df['Gross Profit'] >= profit_range[0]) &
        (df['Gross Profit'] <= profit_range[1])]

# -------------------------
# 📌 KPIs
# -------------------------
st.subheader("📌 Key Metrics")

col1, col2 = st.columns(2)

col1.metric("Total Sales", f"{df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"{df['Gross Profit'].sum():,.0f}")

# -------------------------
# 🏆 Product Profitability
# -------------------------
st.subheader("🏆 Product Profitability")

top_products = df.groupby('Product Name')['Gross Profit'].sum() \
    .sort_values(ascending=False).head(10).reset_index()

col1, col2 = st.columns(2)

# Donut Chart
with col1:
    fig = px.pie(
        top_products,
        values='Gross Profit',
        names='Product Name',
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    st.plotly_chart(fig, width='stretch')

# Bar Chart
with col2:
    fig = px.bar(
        top_products,
        x='Product Name',
        y='Gross Profit',
        color='Gross Profit',
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig, width='stretch')

# -------------------------
# 🏢# -------------------------
# 🏢 Division Performance
# -------------------------
st.subheader("🏢 Division Performance")

division_data = df.groupby('Division')['Gross Profit'].sum().reset_index()

# Custom Colors
color_map = {
    "Chocolate": "#8B4513",   # Brown
    "Sugar": "#FF69B4",       # Pink
    "Other": "#1E90FF"        # Blue
}

fig = px.bar(
    division_data,
    x='Division',
    y='Gross Profit',
    color='Division',
    color_discrete_map=color_map   # 🔥 Custom colors applied
)

st.plotly_chart(fig, width='stretch')
# ⚠️ Cost vs Sales Analysis
# -------------------------
st.subheader("⚠️ Cost vs Sales Analysis")

fig = px.scatter(
    df,
    x='Cost',
    y='Sales',
    size='Gross Profit',
    color='Division',
    hover_name='Product Name',
    color_discrete_sequence=px.colors.qualitative.Bold
)

st.plotly_chart(fig, width='stretch')

# -------------------------
# 📈 Pareto Analysis
# -------------------------
st.subheader("📈 Pareto Analysis (80/20 Rule)")

pareto = df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False)
cum_profit = pareto.cumsum() / pareto.sum()

fig = go.Figure()

fig.add_bar(x=pareto.index, y=pareto.values, name="Profit")

fig.add_scatter(x=pareto.index, y=cum_profit, name="Cumulative %", yaxis="y2")

fig.update_layout(
    yaxis2=dict(overlaying='y', side='right')
)

st.plotly_chart(fig, width='stretch')

# -------------------------
# 📄 Filtered Data Table
# -------------------------
st.subheader("📄 Filtered Data View")

# Show limited columns (clean look)
columns_to_show = [
    'Order Date', 'Division', 'Product Name',
    'Sales', 'Cost', 'Gross Profit', 'Gross Margin (%)'
]

st.dataframe(df[columns_to_show], use_container_width=True)