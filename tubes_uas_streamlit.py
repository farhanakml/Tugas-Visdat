import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(
    page_title="Dashboard Spotify Dataset Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# Load data
df = pd.read_csv("songs_normalize.csv")

# Drop duplicates, keeping the row with the maximum popularity
df = df.loc[df.groupby(['artist', 'song'])['popularity'].idxmax()]

# Optionally drop any remaining duplicates (if you want to ensure no duplicates exist after the operation)
df = df.drop_duplicates()
df = df[df['genre'] != 'set()']
df['genre'] = df['genre'].str.split(r'[;,]\s*')

df['duration'] = df['duration_ms'] / 60000  # Convert duration from milliseconds to minutes



st.markdown(""" 
    <style>
    @font-face {
        font-family: 'Gotham';
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
        font-family: 'GothamBold', sans-serif;
        width: 100%;
        height: 40px;
        border-radius: 20px;
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

if 'show_search' not in st.session_state:
    st.session_state.show_search = False

# Sidebar content
with st.sidebar:
    st.image('spotify-logo.png')

    if st.button("Home"):
        st.session_state.show_search = False

    if st.button("Search"):
        st.session_state.show_search = True

    # Filters section
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
        genre_filter = df['genre'].explode().unique()  # Select all genres from the list
    else:
        genre_filter = st.multiselect(
            "Select Genre(s)",
            options=df['genre'].explode().unique(),
            default=[],
            help="Search and select one or multiple genres"
        )

    # Apply filters to the DataFrame
    filtered_df = df[
        (df['year'] >= year_filter[0]) &  # Filter by start year
        (df['year'] <= year_filter[1]) &  # Filter by end year
        (df['genre'].apply(lambda x: any(g in genre_filter for g in x)))  # Filter by selected genres
    ]

# Filtered data
df = filtered_df

# Render content based on the show_search state
if st.session_state.show_search:
    st.markdown('<p class="title">Search Songs/Artist</p>', unsafe_allow_html=True)
    search_term = st.text_input("Search", placeholder="Type a song or artist name...")

    if search_term:  # Ensure there's a search term entered
        search_results = df[df['artist'].str.contains(search_term, case=False, na=False) |
                            df['song'].str.contains(search_term, case=False, na=False) |
                            df['genre'].apply(lambda genres: any(search_term.lower() in genre.lower() for genre in genres))]

        # Convert 'genre' column from list to string for processing
        search_results['genre_str'] = search_results['genre'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

        # Display search results
        st.markdown(f"### Search Results for: **{search_term}**")
        
        if not search_results.empty:
            # Show search result as a selectbox for selecting a song
            st.markdown("#### Songs in Search Results:")
            
            # For each song in the search result, show the details in an expander
            for idx, row in search_results.iterrows():
                with st.expander(f"🎵 {row['song']} - {row['artist']}"):
                    st.write(f"**Artist**: {row['artist']}")
                    st.write(f"**Song**: {row['song']}")
                    st.write(f"**Duration (ms)**: {row['duration_ms']}")
                    st.write(f"**Explicit**: {'Yes' if row['explicit'] else 'No'}")
                    st.write(f"**Year**: {row['year']}")
                    st.write(f"**Popularity**: {row['popularity']}")
                    st.write(f"**Danceability**: {row['danceability']}")
                    st.write(f"**Energy**: {row['energy']}")
                    st.write(f"**Key**: {row['key']}")
                    st.write(f"**Loudness**: {row['loudness']}")
                    st.write(f"**Mode**: {row['mode']}")
                    st.write(f"**Speechiness**: {row['speechiness']}")
                    st.write(f"**Acousticness**: {row['acousticness']}")
                    st.write(f"**Instrumentalness**: {row['instrumentalness']}")
                    st.write(f"**Liveness**: {row['liveness']}")
                    st.write(f"**Valence**: {row['valence']}")
                    st.write(f"**Tempo**: {row['tempo']}")
                    st.write(f"**Genre(s)**: {', '.join(row['genre'])}")
        else:
            st.markdown("**No results found.**")
    else:
        st.markdown("**Please enter a search term.**")
else:
    st.markdown('<p class="main-title">Spotify Dataset Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="title">Dataset Information</p>', unsafe_allow_html=True)

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
    total_genres = df['genre'].explode().nunique()
        
    with col1:
        st.markdown(f'<p class="subtitle">Total Songs<br><span class="number">{total_songs}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Total Artists<br><span class="number">{total_artists}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Total Genres<br><span class="number">{total_genres}</span></p>', unsafe_allow_html=True)

    with col2:
        genre_count = df.explode('genre').groupby('genre').size().reset_index(name='song_count')
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
        st.markdown('<p class="subtitle">Top Artists by Number of Songs</p>', unsafe_allow_html=True)
        # Total songs per artist
        artist_song_count = df.groupby('artist').size().reset_index(name='song_count')
        top_artists_by_songs = artist_song_count.sort_values(by='song_count', ascending=False).head(5)  # Top 5 artists

        artist_chart = alt.Chart(top_artists_by_songs).mark_bar(color='green').encode(
            x=alt.X('song_count:Q', title='Number of Songs'),
            y=alt.Y('artist:N', sort='-x', title='Artist'),
            tooltip=['artist:N', 'song_count:Q']
        ).properties(
            width=400,
            height=300
        )

        st.altair_chart(artist_chart, use_container_width=True)

    with col2:
        st.markdown('<p class="subtitle">Total Songs Released Per Year</p>', unsafe_allow_html=True)
        # Group data by year to calculate the number of songs and average popularity
        annual_trends = df.groupby('year').agg(
            total_songs=('song', 'count'),
            avg_popularity=('popularity', 'mean')
        ).reset_index()

        # Line chart for the total number of songs released per year
        songs_trend_chart = alt.Chart(annual_trends).mark_line(color='green', point=True).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('total_songs:Q', title='Total Songs Released'),
            tooltip=['year:O', 'total_songs:Q']
        ).properties(
            width=600,
            height=300
        )
        st.altair_chart(songs_trend_chart, use_container_width=True)
