import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
from datetime import datetime
import calendar as cal

st.set_page_config(
    page_title="Dashboard Spotify Dataset Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# Load data
df = pd.read_csv("songs_normalize.csv")
df = df[df['genre'] != 'set()']
# Pisahkan genre berdasarkan delimiters koma atau titik koma
df['genre'] = df['genre'].str.split(r'[;,]\s*')

# Ekspansi genre menjadi baris terpisah
df = df.explode('genre')

df['duration'] = df['duration_ms'] / 60000

st.markdown("""
    <style>
    @font-face {
        font-family: 'GothamBold';
        src: url('fonts/GothamMedium.ttf') format('truetype');
        font-weight: bold;
        font-style: normal;
    }
    body {
        font-family: 'Gotham', sans-serif;
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        font-family: 'Gotham', sans-serif;
    }
    .title {
        font-family: 'Gotham', sans-serif;
        color: white;
        font-size: 26px;
        font-weight: bold;
    }
    .main-title {
        font-family: 'Gotham', sans-serif;
        color: white;
        font-size: 40px;
        font-weight: bold;
    }
    .subtitle{
        font-family: 'Gotham', sans-serif;
        color: white;
        font-size: 18px;
    }
    .number{
        font-family: 'Gotham', sans-serif;
        color: white;
        font-size: 26px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title"> Spotify Dataset Dashboard</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image('spotify-logo.png')
    col1, col2 = st.columns((2, 4))
    with col1:
        st.markdown('<p class="title">phaaa</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="title">test</p>', unsafe_allow_html=True)
    # Add a subtitle for filters
    show_search = st.checkbox("Search for Song/Artist", value=False)  # Initially hidden
    st.subheader("Filters")

    # Filter by year range using a slider
    year_filter = st.slider(
        "Select Year Range",
        min_value=int(df['year'].min()),  # Dynamically set min year
        max_value=int(df['year'].max()),  # Dynamically set max year
        value=(int(df['year'].min()), int(df['year'].max()))  # Default to full range
    )
    
    # Filter by genre using multiselect
    select_all = st.checkbox("Select All Genres", value=True)
    if select_all:
        genre_filter = df['genre'].unique()  # Select all genres
    else:
        genre_filter = st.multiselect(
            "Select Genre(s)",
            options=df['genre'].unique(),
            default=[],
            help="Search and select one or multiple genres"
        )

    
    # Apply filters to the DataFrame
    filtered_df = df[
        (df['year'] >= year_filter[0]) &  # Filter by start year
        (df['year'] <= year_filter[1]) &  # Filter by end year
        (df['genre'].isin(genre_filter))  # Filter by selected genres
    ]

df = filtered_df

if show_search:
        search_term = st.text_input("Search", placeholder="Type a song or artist name...")
        if st.button("Search"):
            search_results = df[df['artist'].str.contains(search_term, case=False, na=False) | 
                                df['song'].str.contains(search_term, case=False, na=False)]
            
            # Display search results
            st.markdown(f"### Search Results for: **{search_term}**")
            if not search_results.empty:
                # Ensure the dataframe takes up the full width of the page
                st.dataframe(search_results[['artist', 'song', 'genre', 'year', 'popularity']], use_container_width=True)
            else:
                st.markdown("**No results found.**")

else:
    st.markdown('<p class="title"> Dataset Information </p>', unsafe_allow_html=True)

    def make_donut(explicit_count, non_explicit_count, input_color):
        if input_color == 'green':
            chart_color = ['#E74C3C', '#008000']

        total = explicit_count + non_explicit_count
        explicit_percentage = explicit_count / total * 100
        non_explicit_percentage = non_explicit_count / total * 100

        source = pd.DataFrame({
            "Status": ["Explicit", "Non-Explicit"],
            "Value": [explicit_count, non_explicit_count],
            "Percentage": [explicit_percentage, non_explicit_percentage]
        })

        plot = alt.Chart(source).mark_arc(innerRadius=70, outerRadius=85, cornerRadius=10).encode(
            theta=alt.Theta(field="Value", type="quantitative"),
            color=alt.Color("Status:N",
                            scale=alt.Scale(
                                domain=["Explicit", "Non-Explicit"],
                                range=chart_color),
                            legend=None),
            tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Value:Q"), alt.Tooltip("Percentage:Q", format=".1f")]
        ).properties(width=220, height=220)

        text = alt.Chart(pd.DataFrame({'text': [f'{non_explicit_percentage:.1f}%']})).mark_text(
            align='center', fontSize=30, fontWeight=600, color='#008000'
        ).encode(
            text='text:N'
        ).properties(width=220, height=220)

        return plot + text


    col1, col2, col3 = st.columns((1, 3, 2), gap='large')

    df = filtered_df

    total_songs = df.shape[0]
    total_artists = df['artist'].nunique()
    total_genres = df['genre'].nunique()
        
    with col1:
        # st.metric('Total Songs', value=total_songs)
        st.markdown(f'<p class="subtitle">Total Songs<br><span class="number">{total_songs}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Total Artists<br><span class="number">{total_artists}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Total Genres<br><span class="number">{total_genres}</span></p>', unsafe_allow_html=True)

        
    with col2:
        genre_count = df.groupby('genre').size().reset_index(name='song_count')
        top_10_genres = genre_count.sort_values(by='song_count', ascending=False).head(8)

        # Create the Altair bar chart
        st.markdown('<p class="subtitle"> Number of Songs per Genre </p>', unsafe_allow_html=True)
        genre_chart = alt.Chart(top_10_genres).mark_bar(color='green').encode(
            x=alt.X('genre:N', title='Genre', sort='-y'),
            y=alt.Y('song_count:Q', title='Number of Songs'),
            tooltip=['genre:N', 'song_count:Q']
        ).properties(
            width=500,
            height=280
        ).configure_title(
            fontSize=20,
            anchor='start',
            font='Arial'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
    )
        st.altair_chart(genre_chart, use_container_width=True)
        
    with col3:
        st.markdown('<p class="subtitle"> Non-Explicit Songs Percentage </p>', unsafe_allow_html=True)
        explicit_count = df[df['explicit'] == True].shape[0]  # Count where explicit is True
        non_explicit_count = df[df['explicit'] == False].shape[0]  # Count where explicit is False
        # Create the chart with green color scheme
        donut_chart = make_donut(explicit_count, non_explicit_count, 'green')
        donut_chart  

    col1, col2= st.columns((5, 5), gap='large')

    with col1:
        st.write('a')

    with col2:
        st.write('b')
