import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

# Set Streamlit page config as the FIRST Streamlit command
st.set_page_config(layout="wide", page_title="Global Economic & Human Development Dashboard")

warnings.filterwarnings("ignore")

# Load Data
@st.cache_data
def load_data():
    gdp = pd.read_excel("./World+Economic+Indicators/WorldBank.xlsx")
    hdi = pd.read_csv("./World+Economic+Indicators/HDI.csv")
    return gdp, hdi

gdp, hdi = load_data()

st.title("🌍 Global Economic & Human Development Dashboard")


# ===================== Q1.1: GDP Growth =====================
st.header("1.1: Countries with Highest GDP Growth")

gdp['Population'] = gdp['GDP (USD)'] / gdp['GDP per capita (USD)']
gdp = gdp.sort_values(['Country Name', 'Year'])
gdp["GDP Growth (%)"] = gdp.groupby('Country Name')['GDP (USD)'].pct_change() * 100
gdp["Population Growth (%)"] = gdp.groupby('Country Name')['Population'].pct_change() * 100
avg_gdp_growth = gdp.groupby('Country Name')['GDP Growth (%)'].mean().sort_values(ascending=False).reset_index()
top_country_gdp = avg_gdp_growth.loc[avg_gdp_growth['GDP Growth (%)'].idxmax()]

fig_gdp = px.choropleth(
    avg_gdp_growth,
    locations='Country Name',
    locationmode='country names',
    color='GDP Growth (%)',
    hover_name='Country Name',
    color_continuous_scale='Inferno',
    title='Average GDP Growth by Country (%)'
)
fig_gdp.update_layout(
    annotations=[dict(
        text=f"🌟 <b>Top Country:</b> {top_country_gdp['Country Name']}<br><b>Avg GDP Growth:</b> {top_country_gdp['GDP Growth (%)']:.2f}%",
        x=0.5, y=-0.15, xref='paper', yref='paper',
        showarrow=False, font=dict(size=14, color='white'),
        align='center', bgcolor='black', bordercolor='white',
        borderwidth=1, borderpad=10
    )]
)
fig_gdp.update_geos(showcountries=True, showcoastlines=True, showframe=False)
fig_gdp.update_layout(coloraxis_colorbar=dict(title='Avg GDP Growth %'))
st.plotly_chart(fig_gdp)

# ===================== Q1.2: Population Growth =====================
st.header("1.2: Countries with Highest Population Growth")

avg_population_growth = gdp.groupby('Country Name')['Population Growth (%)'].mean().sort_values(ascending=False).reset_index()
top_country_pop = avg_population_growth.loc[avg_population_growth['Population Growth (%)'].idxmax()]

fig_pop = px.choropleth(
    avg_population_growth,
    locations='Country Name',
    locationmode='country names',
    color='Population Growth (%)',
    hover_name='Country Name',
    color_continuous_scale='Inferno',
    title='Average Population Growth by Country (%)'
)
fig_pop.update_layout(
    annotations=[dict(
        text=f"🌟 <b>Top Country:</b> {top_country_pop['Country Name']}<br><b>Avg Population Growth:</b> {top_country_pop['Population Growth (%)']:.2f}%",
        x=0.5, y=-0.15, xref='paper', yref='paper',
        showarrow=False, font=dict(size=14, color='white'),
        align='center', bgcolor='black', bordercolor='white',
        borderwidth=1, borderpad=10
    )]
)
fig_pop.update_geos(showcountries=True, showcoastlines=True, showframe=False)
fig_pop.update_layout(coloraxis_colorbar=dict(title='Avg Population Growth %'))
st.plotly_chart(fig_pop)

# ===================== Q1.3: Overlap Analysis =====================
st.header("1.3: Is there overlap between GDP & Population Growth?")

top_10_gdp_growth = avg_gdp_growth.head(10)
top_10_population_growth = avg_population_growth.head(10)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 GDP Growth Countries")
    st.dataframe(top_10_gdp_growth)
with col2:
    st.subheader("Top 10 Population Growth Countries")
    st.dataframe(top_10_population_growth)

# ===================== Q2: HDI Growth by Region =====================
st.header("2: HDI Growth by Region (2000–2021)")

hdi['region'] = hdi['region'].map({
    'SA': 'South Asia',
    'SSA': 'Sub-Saharan Africa',
    'ECA': 'Europe and Central Asia',
    'AS': 'Arab States',
    'LAC': 'Latin America and the Caribbean',
    'EAP': 'East Asia and the Pacific'
})
hdi['hdi_growth_21st_century'] = hdi['hdi_2021'] - hdi['hdi_2000']
hdi_growth = hdi.groupby('region')['hdi_growth_21st_century'].mean().sort_values(ascending=False).head(5)

labels = hdi_growth.index.tolist()
values = hdi_growth.values.tolist()
pull = [0.1] + [0 for _ in range(len(labels) - 1)]

fig_hdi = go.Figure(data=[go.Pie(
    labels=labels, values=values, hole=0.5, pull=pull,
    textinfo='label+percent',
    marker=dict(colors=px.colors.qualitative.Set3)
)])
fig_hdi.update_layout(
    title_text='Top 5 Regions by Average HDI Growth (2000–2021)',
    annotations=[dict(text='HDI Growth', x=0.5, y=0.5, font_size=16, showarrow=False)]
)
st.plotly_chart(fig_hdi)

# ===================== Q3: Correlation with Life Expectancy =====================
st.header("3: Factors Correlated with Life Expectancy")

gdp_for_life = gdp.copy()
gdp_for_life.drop(['Country Name', 'Country Code', 'Region', 'Year', 'Population', 'GDP Growth (%)', 'Population Growth (%)'], axis=1, inplace=True)
gdp_for_life.fillna(0, inplace=True)
gdp_for_life = pd.get_dummies(gdp_for_life, drop_first=True).astype(float)

corr_life = gdp_for_life.corr()
target_corr_life = corr_life['Life expectancy at birth (years)'].drop('Life expectancy at birth (years)').sort_values(ascending=False)

target_corr_df = target_corr_life.reset_index()
target_corr_df.columns = ['Feature', 'Correlation']

fig_corr_life = px.bar(
    target_corr_df,
    x='Correlation', y='Feature',
    orientation='h',
    color='Correlation',
    color_continuous_scale='RdBu',
    title='Correlation with Life Expectancy at Birth',
    text=target_corr_df['Correlation'].round(3)
)
fig_corr_life.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig_corr_life.update_layout(yaxis=dict(autorange='reversed'), xaxis_title='Correlation Coefficient')
st.plotly_chart(fig_corr_life)

# ===================== Q4: High Income vs Low Income =====================
st.header("4: Factors Differentiating High vs Low Income Countries")

gdp_income = gdp.copy()
gdp_income.drop(['Country Name', 'Country Code', 'Region', 'Year', 'Population', 'GDP Growth (%)', 'Population Growth (%)'], axis=1, inplace=True)
gdp_income['IncomeGroup'] = gdp_income['IncomeGroup'].map({
    'Upper middle income': 'High Income',
    'Lower middle income': 'Low Income',
    'High income: nonOECD': 'High Income',
    'High income: OECD': 'High Income',
    'Low income': 'Low Income'
})
gdp_income.fillna(0, inplace=True)
gdp_income = pd.get_dummies(gdp_income, drop_first=True).astype(float)

corr_income = gdp_income.corr()
target_corr_income = corr_income['IncomeGroup_Low Income'].drop('IncomeGroup_Low Income').sort_values(ascending=False)

target_corr_df_income = target_corr_income.reset_index()
target_corr_df_income.columns = ['Feature', 'Correlation']

fig_corr_income = px.bar(
    target_corr_df_income,
    x='Correlation', y='Feature',
    orientation='h',
    color='Correlation',
    color_continuous_scale='RdBu',
    title='Correlation with Low Income Group',
    text=target_corr_df_income['Correlation'].round(3)
)
fig_corr_income.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig_corr_income.update_layout(yaxis=dict(autorange='reversed'), xaxis_title='Correlation Coefficient')
st.plotly_chart(fig_corr_income)  