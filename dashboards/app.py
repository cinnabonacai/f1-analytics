"""
Formula 1 Analytics Dashboard
Interactive Streamlit dashboard for F1 performance analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_cleaner import F1DataCleaner

# Page configuration
st.set_page_config(
    page_title="Formula 1 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #E10600;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load and clean F1 data"""
    data_dir = Path("../data")
    cleaner = F1DataCleaner(data_dir=data_dir)
    cleaner.load_data()
    cleaner.clean_races()
    cleaner.clean_drivers()
    cleaner.clean_results()
    cleaner.clean_qualifying()
    cleaner.clean_pitstops()
    merged_df = cleaner.merge_data()
    aggregated = cleaner.create_aggregated_tables()
    return cleaner, merged_df, aggregated

# Main app
def main():
    st.markdown('<h1 class="main-header">🏎️ Formula 1 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading F1 data..."):
        cleaner, merged_df, aggregated = load_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🏁 Driver Insights", "🏎️ Constructor Comparison", "⏱️ Pit Stop Analysis", "🌦️ Circuit & Weather Impact"]
    )
    
    # Year filter
    years = sorted(merged_df['year'].unique(), reverse=True)
    selected_years = st.sidebar.multiselect(
        "Select Years",
        years,
        default=years[:10] if len(years) > 10 else years
    )
    
    if not selected_years:
        st.warning("Please select at least one year")
        return
    
    filtered_df = merged_df[merged_df['year'].isin(selected_years)]
    
    # Page routing
    if page == "🏁 Driver Insights":
        driver_insights_page(cleaner, filtered_df, aggregated)
    elif page == "🏎️ Constructor Comparison":
        constructor_comparison_page(cleaner, filtered_df, aggregated)
    elif page == "⏱️ Pit Stop Analysis":
        pitstop_analysis_page(cleaner, filtered_df)
    elif page == "🌦️ Circuit & Weather Impact":
        circuit_analysis_page(cleaner, filtered_df)


def driver_insights_page(cleaner, df, aggregated):
    """Driver insights page"""
    st.header("🏁 Driver Performance Insights")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    driver_stats = aggregated['driver_stats'].copy()
    top_driver = driver_stats.nlargest(1, 'wins').iloc[0]
    
    with col1:
        st.metric("Top Driver (Wins)", top_driver['full_name'], f"{int(top_driver['wins'])} wins")
    with col2:
        st.metric("Total Drivers", len(driver_stats), f"{df['driverId'].nunique()} in selected period")
    with col3:
        avg_points = driver_stats['total_points'].mean()
        st.metric("Avg Points/Driver", f"{avg_points:.0f}", f"Max: {driver_stats['total_points'].max():.0f}")
    with col4:
        avg_win_rate = driver_stats['win_rate'].mean() * 100
        st.metric("Avg Win Rate", f"{avg_win_rate:.2f}%", f"Top: {driver_stats['win_rate'].max()*100:.2f}%")
    
    # Top drivers chart
    st.subheader("Top Drivers by Wins")
    top_n = st.slider("Number of drivers to show", 5, 20, 10)
    top_drivers = driver_stats.nlargest(top_n, 'wins')
    
    fig = px.bar(
        top_drivers,
        x='wins',
        y='full_name',
        orientation='h',
        color='wins',
        color_continuous_scale='Reds',
        labels={'wins': 'Number of Wins', 'full_name': 'Driver'},
        title=f'Top {top_n} Drivers by Race Wins'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Driver comparison
    st.subheader("Compare Drivers")
    driver_list = sorted(driver_stats['full_name'].dropna().unique())
    selected_drivers = st.multiselect("Select drivers to compare", driver_list, default=driver_list[:3])
    
    if selected_drivers:
        compare_df = driver_stats[driver_stats['full_name'].isin(selected_drivers)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                compare_df,
                x='full_name',
                y=['wins', 'podiums'],
                barmode='group',
                title='Wins vs Podiums',
                labels={'value': 'Count', 'full_name': 'Driver'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                compare_df,
                x='win_rate',
                y='podium_rate',
                size='total_points',
                text='full_name',
                title='Win Rate vs Podium Rate',
                labels={'win_rate': 'Win Rate', 'podium_rate': 'Podium Rate'}
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
    
    # Driver performance over time
    st.subheader("Driver Performance Trends")
    selected_driver = st.selectbox("Select driver", driver_list)
    
    if selected_driver:
        driver_id = driver_stats[driver_stats['full_name'] == selected_driver]['driverId'].values[0]
        driver_history = df[df['driverId'] == driver_id].groupby('year').agg({
            'points': 'sum',
            'position': 'mean',
            'position': lambda x: (x == 1).sum()  # Wins
        }).reset_index()
        driver_history.columns = ['year', 'points', 'avg_position', 'wins']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=driver_history['year'], y=driver_history['points'], name="Points", line=dict(color='blue')),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=driver_history['year'], y=driver_history['wins'], name="Wins", line=dict(color='red')),
            secondary_y=True
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Points", secondary_y=False)
        fig.update_yaxes(title_text="Wins", secondary_y=True)
        fig.update_layout(title=f"{selected_driver} - Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)


def constructor_comparison_page(cleaner, df, aggregated):
    """Constructor comparison page"""
    st.header("🏎️ Constructor Performance Comparison")
    
    constructor_stats = aggregated['constructor_stats'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    top_constructor = constructor_stats.nlargest(1, 'wins').iloc[0]
    
    with col1:
        st.metric("Top Constructor", top_constructor['name'], f"{int(top_constructor['wins'])} wins")
    with col2:
        st.metric("Total Constructors", len(constructor_stats), f"{df['constructorId'].nunique()} in period")
    with col3:
        avg_points = constructor_stats['total_points'].mean()
        st.metric("Avg Points/Constructor", f"{avg_points:.0f}", f"Max: {constructor_stats['total_points'].max():.0f}")
    with col4:
        avg_win_rate = constructor_stats['win_rate'].mean() * 100
        st.metric("Avg Win Rate", f"{avg_win_rate:.2f}%", f"Top: {constructor_stats['win_rate'].max()*100:.2f}%")
    
    # Top constructors
    st.subheader("Top Constructors by Wins")
    top_n = st.slider("Number of constructors to show", 5, 20, 10, key="constructor_slider")
    top_constructors = constructor_stats.nlargest(top_n, 'wins')
    
    fig = px.bar(
        top_constructors,
        x='wins',
        y='name',
        orientation='h',
        color='wins',
        color_continuous_scale='Blues',
        labels={'wins': 'Number of Wins', 'name': 'Constructor'},
        title=f'Top {top_n} Constructors by Race Wins'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Constructor comparison
    st.subheader("Compare Constructors")
    constructor_list = sorted(constructor_stats['name'].dropna().unique())
    selected_constructors = st.multiselect("Select constructors", constructor_list, default=constructor_list[:3])
    
    if selected_constructors:
        compare_df = constructor_stats[constructor_stats['name'].isin(selected_constructors)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                compare_df,
                x='name',
                y=['wins', 'podiums'],
                barmode='group',
                title='Wins vs Podiums',
                labels={'value': 'Count', 'name': 'Constructor'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                compare_df,
                x='win_rate',
                y='podium_rate',
                size='total_points',
                text='name',
                title='Win Rate vs Podium Rate',
                labels={'win_rate': 'Win Rate', 'podium_rate': 'Podium Rate'}
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
    
    # Constructor trends over time
    st.subheader("Constructor Performance Over Time")
    selected_constructor = st.selectbox("Select constructor", constructor_list)
    
    if selected_constructor:
        constructor_id = constructor_stats[constructor_stats['name'] == selected_constructor]['constructorId'].values[0]
        constructor_history = df[df['constructorId'] == constructor_id].groupby('year').agg({
            'points': 'sum',
            'position': lambda x: (x == 1).sum()
        }).reset_index()
        constructor_history.columns = ['year', 'points', 'wins']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=constructor_history['year'], y=constructor_history['points'], name="Points", line=dict(color='blue')),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=constructor_history['year'], y=constructor_history['wins'], name="Wins", line=dict(color='red')),
            secondary_y=True
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Points", secondary_y=False)
        fig.update_yaxes(title_text="Wins", secondary_y=True)
        fig.update_layout(title=f"{selected_constructor} - Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)


def pitstop_analysis_page(cleaner, df):
    """Pit stop analysis page"""
    st.header("⏱️ Pit Stop Strategy Analysis")
    
    if cleaner.pitstops is None or cleaner.pitstops.empty:
        st.warning("Pit stop data not available for the selected period")
        return
    
    # KPIs
    pit_df = cleaner.pitstops.copy()
    pit_df = pit_df[pit_df['year'].isin(df['year'].unique())]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_duration = pit_df['duration_seconds'].mean()
        st.metric("Avg Pit Duration", f"{avg_duration:.2f}s", f"Fastest: {pit_df['duration_seconds'].min():.2f}s")
    with col2:
        total_stops = len(pit_df)
        st.metric("Total Pit Stops", f"{total_stops:,}", f"Avg per race: {total_stops/df['raceId'].nunique():.1f}")
    with col3:
        median_duration = pit_df['duration_seconds'].median()
        st.metric("Median Duration", f"{median_duration:.2f}s", f"Slowest: {pit_df['duration_seconds'].max():.2f}s")
    with col4:
        avg_stops_per_race = pit_df.groupby(['raceId', 'year', 'driverId']).size().mean()
        st.metric("Avg Stops/Race", f"{avg_stops_per_race:.1f}", "Per driver")
    
    # Distribution
    st.subheader("Pit Stop Duration Distribution")
    fig = px.histogram(
        pit_df,
        x='duration_seconds',
        nbins=50,
        title='Distribution of Pit Stop Durations',
        labels={'duration_seconds': 'Duration (seconds)', 'count': 'Frequency'}
    )
    fig.add_vline(x=avg_duration, line_dash="dash", line_color="red", annotation_text=f"Mean: {avg_duration:.2f}s")
    st.plotly_chart(fig, use_container_width=True)
    
    # Trends over time
    st.subheader("Pit Stop Trends Over Time")
    pit_by_year = pit_df.groupby('year').agg({
        'duration_seconds': 'mean',
        'stop': 'count'
    }).reset_index()
    pit_by_year.columns = ['year', 'avg_duration', 'total_stops']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=pit_by_year['year'], y=pit_by_year['avg_duration'], name="Avg Duration", line=dict(color='red')),
        secondary_y=False
    )
    fig.add_trace(
        go.Bar(x=pit_by_year['year'], y=pit_by_year['total_stops'], name="Total Stops", marker_color='blue', opacity=0.5),
        secondary_y=True
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Avg Duration (seconds)", secondary_y=False)
    fig.update_yaxes(title_text="Total Stops", secondary_y=True)
    fig.update_layout(title="Pit Stop Duration and Frequency Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Pit stops by driver
    st.subheader("Pit Stop Performance by Driver")
    pit_by_driver = pit_df.groupby('driverId')['duration_seconds'].mean().reset_index()
    pit_by_driver = pit_by_driver.merge(
        cleaner.drivers[['driverId', 'full_name']],
        on='driverId',
        how='left'
    )
    pit_by_driver = pit_by_driver.sort_values('duration_seconds').head(20)
    
    fig = px.bar(
        pit_by_driver,
        x='duration_seconds',
        y='full_name',
        orientation='h',
        title='Top 20 Drivers by Average Pit Stop Speed (Fastest)',
        labels={'duration_seconds': 'Avg Duration (seconds)', 'full_name': 'Driver'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)


def circuit_analysis_page(cleaner, df):
    """Circuit and weather analysis page"""
    st.header("🌦️ Circuit & Weather Impact Analysis")
    
    if 'circuit_name' not in df.columns:
        st.warning("Circuit data not available")
        return
    
    # Circuit statistics
    circuit_stats = df.groupby('circuit_name').agg({
        'raceId': 'nunique',
        'position': 'mean',
        'points': 'sum'
    }).reset_index()
    circuit_stats.columns = ['circuit', 'races', 'avg_position', 'total_points']
    circuit_stats = circuit_stats.sort_values('races', ascending=False)
    
    st.subheader("Circuit Statistics")
    top_n_circuits = st.slider("Number of circuits to show", 5, 30, 15, key="circuit_slider")
    top_circuits = circuit_stats.head(top_n_circuits)
    
    fig = px.bar(
        top_circuits,
        x='races',
        y='circuit',
        orientation='h',
        color='races',
        color_continuous_scale='Viridis',
        title=f'Top {top_n_circuits} Circuits by Number of Races Hosted',
        labels={'races': 'Number of Races', 'circuit': 'Circuit'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Qualifying vs Race Performance
    st.subheader("Qualifying vs Race Performance")
    qual_race_data = df[['qualifying_position', 'position', 'circuit_name']].copy()
    qual_race_data = qual_race_data.dropna(subset=['qualifying_position', 'position'])
    
    if not qual_race_data.empty:
        correlation = qual_race_data['qualifying_position'].corr(qual_race_data['position'])
        st.metric("Correlation", f"{correlation:.3f}", "Higher = stronger predictor")
        
        fig = px.scatter(
            qual_race_data,
            x='qualifying_position',
            y='position',
            color='circuit_name',
            title='Qualifying Position vs Final Race Position',
            labels={'qualifying_position': 'Qualifying Position', 'position': 'Final Position'},
            opacity=0.6
        )
        fig.add_trace(go.Scatter(
            x=[1, 20], y=[1, 20],
            mode='lines',
            name='Perfect Correlation',
            line=dict(dash='dash', color='black')
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # DNF Analysis by Circuit
    st.subheader("DNF Rate by Circuit")
    dnf_by_circuit = df.groupby('circuit_name').agg({
        'is_dnf': ['sum', 'mean', 'count']
    }).reset_index()
    dnf_by_circuit.columns = ['circuit', 'total_dnfs', 'dnf_rate', 'races']
    dnf_by_circuit = dnf_by_circuit[dnf_by_circuit['races'] >= 5].sort_values('dnf_rate', ascending=False).head(15)
    
    fig = px.bar(
        dnf_by_circuit,
        x='dnf_rate',
        y='circuit',
        orientation='h',
        title='Top 15 Circuits by DNF Rate (Min 5 races)',
        labels={'dnf_rate': 'DNF Rate', 'circuit': 'Circuit'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

