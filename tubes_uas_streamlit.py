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
        font-family: 'Poppins';
        src: url('fonts/Poppins-Medium.ttf') format('truetype');
        font-weight: bold;
        font-style: normal;
    }
    body {
        font-family: 'Poppins', sans-serif ;
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        font-family: 'Poppins';
        width: 100%;
        height: 40px;
        border-radius: 20px;
    }
    .title {
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 26px;
        font-weight: bold;
    }
    .main-title {
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 36px;
        font-weight: bold;
    }
    .subtitle{
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 18px;
    }
    .number{
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 26px;
    }
    .belowtitle{
        font-family: 'Poppins', sans-serif;
        color: white;
        font-size: 24px;
    }
    .header-container img {
        height: 50px; /* Adjust the size of the image */
    }
    </style>
    """, unsafe_allow_html=True)

if 'show_search_songs' not in st.session_state:
    st.session_state.show_search_songs = False

if 'show_search_artists' not in st.session_state:
    st.session_state.show_search_artists = False

if 'show_about' not in st.session_state:
    st.session_state.show_about = False

# Sidebar content
with st.sidebar:
    st.image('spotify-logo.png')

    if st.button("Home"):
        st.session_state.show_search_songs = False
        st.session_state.show_search_artists = False
        st.session_state.show_about = False

    if st.button("Search Songs"):
        st.session_state.show_search_songs = True
        st.session_state.show_search_artists = False
        st.session_state.show_about = False

    if st.button("Search Artists"):
        st.session_state.show_search_songs = False
        st.session_state.show_search_artists = True
        st.session_state.show_about = False 

    if st.button("About"):
        st.session_state.show_about = True 
        st.session_state.show_search_songs = False
        st.session_state.show_search_artists = False

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

# Render content based on the show_search_songs state
# Render content based on the show_search_songs state
if st.session_state.show_search_songs:
    st.markdown('<p class="title">Search Songs</p>', unsafe_allow_html=True)
    search_term = st.text_input("Search", placeholder="Type a song...")

    if search_term:  # Ensure there's a search term entered
        search_results = df[df['artist'].str.contains(search_term, case=False, na=False) |
                            df['song'].str.contains(search_term, case=False, na=False) |
                            df['genre'].apply(lambda genres: any(search_term.lower() in genre.lower() for genre in genres))]

        # Convert 'genre' column from list to string for processing
        search_results['genre_str'] = search_results['genre'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

        # Display search results
        st.markdown(f"### Search Results for: **{search_term}**")
        
        if not search_results.empty:
            st.markdown("#### Songs in Search Results:")

            # Split search results into pairs
            pairs = [search_results.iloc[i:i+2] for i in range(0, len(search_results), 2)]
            
            # Display the songs in two columns per pair
            for pair in pairs:
                col1, col2 = st.columns(2)  # Create two columns for each pair

                for i, (idx, row) in enumerate(pair.iterrows()):  # Make sure to get both the index and the row
                    # Create a unique key for each song's detail visibility
                    detail_key = f"show_detail_{idx}"  # Use idx for the detail key

                    # Check if this key exists in session state, initialize if not
                    if detail_key not in st.session_state:
                        st.session_state[detail_key] = False

                    # Alternate between columns for each song in the pair
                    with col1 if i == 0 else col2:
                        st.markdown(f"""
                        <div style="background-color:#1DB954; border-radius:15px; padding:8px 15px; margin:10px 0; text-align:left; height:50px; overflow:hidden;">
                            <h5 style="color:white; font-size:18px; margin:0; line-height: 30px;">🎵 {row['song']} - {row['artist']}</h5>
                        </div>
                        """, unsafe_allow_html=True)

                        # Display the detail box, aligned left
                        if st.button("Show More", key=f"{detail_key}_button", help="Click to toggle details"):
                            # Toggle the visibility state for this song's details
                            st.session_state[detail_key] = not st.session_state[detail_key]

                        if st.session_state[detail_key]:
                            st.markdown(f"""
                            <div style="background-color:#222222; border-radius:10px; padding:10px; margin:10px 0; text-align:left;">
                                <h5 style="color:white; font-size:16px;">🎶 Detail Information</h5>
                                <p style="color:white; font-size:14px; margin:0;">
                                    <strong>Title:</strong> {row['song']}<br>
                                    <strong>Artist:</strong> {row['artist']}<br>
                                    <strong>Duration:</strong> {round(row['duration'], 2)} minutes<br>
                                    <strong>Explicit:</strong> {'Yes' if row['explicit'] else 'No'}<br>
                                    <strong>Year Released:</strong> {row['year']}<br>
                                    <strong>Popularity:</strong> {row['popularity']}<br>
                                    <strong>Danceability:</strong> {row['danceability']}<br>
                                    <strong>Energy:</strong> {row['energy']}<br>
                                    <strong>Instrumentalness:</strong> {row['instrumentalness']}<br>
                                    <strong>Genre(s):</strong> {', '.join(row['genre'])}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

        else:
            st.markdown("**No results found.**")
    else:
        st.markdown("**Please enter a search term.**")


elif st.session_state.show_search_artists:
    st.markdown('<p class="title">Search Artists</p>', unsafe_allow_html=True)
    artist_search_term = st.text_input("Search Artists", placeholder="Type an artist's name...")

    if artist_search_term:
        artist_results = filtered_df[
            filtered_df['artist'].str.contains(artist_search_term, case=False, na=False)
        ][['artist']].drop_duplicates()

        if not artist_results.empty:
            selected_artist = st.selectbox("Select an Artist", artist_results['artist'])

            if selected_artist:
                artist_songs = filtered_df[filtered_df['artist'] == selected_artist]

                st.markdown(f"Show Artists Data for : **{selected_artist}**")

                # Render the same graphs as in the "Search Songs" functionality for this artist

                col1, col2, col3 = st.columns([2, 2, 1.4])
                with col1:
                    avg_popularity_chart = alt.Chart(artist_songs).mark_line(point=True, color='#1DB954').encode(
                        x=alt.X('year:O', title='Year'),
                        y=alt.Y('mean(popularity):Q', title='Average Popularity'),
                        tooltip=['year:O', 'mean(popularity):Q']
                    ).properties(
                        width=200,
                        height=250
                    )
                    st.markdown('<p class="subtitle">Average Popularity Across the Years</p>', unsafe_allow_html=True)
                    st.altair_chart(avg_popularity_chart, use_container_width=True)

                    st.markdown('<p class="subtitle">Number of Released Songs per Year</p>', unsafe_allow_html=True)
                    # Group data by year and count the number of songs
                    songs_per_year = artist_songs.groupby('year')['song'].count().reset_index()
                    songs_per_year.columns = ['year', 'num_songs']

                    # Ensure the number of songs is an integer
                    songs_per_year['num_songs'] = songs_per_year['num_songs'].astype(int)

                    # Format 'num_songs' as string for tooltip display (to enforce integer appearance)
                    songs_per_year['num_songs_str'] = songs_per_year['num_songs'].astype(str)

                    # Create a vertical bar chart for number of songs released per year
                    songs_per_year_chart = alt.Chart(songs_per_year).mark_bar(color='#1DB954').encode(
                        x=alt.X('year:O', title='Year'),
                        y=alt.Y('num_songs:Q', title='Number of Songs'),
                        tooltip=[
                            alt.Tooltip('year:O', title='Year'),
                            alt.Tooltip('num_songs_str:N', title='Number of Songs')  # Use string version to guarantee no decimals
                        ]
                    ).properties(
                        width=200,
                        height=250
                    )

                    st.altair_chart(songs_per_year_chart, use_container_width=True)


                # Graph for average duration of songs across the years
                with col2:
                    avg_duration_chart = alt.Chart(artist_songs).mark_line(point=True, color='#1DB954').encode(
                        x=alt.X('year:O', title='Year'),
                        y=alt.Y('mean(duration):Q', title='Average Duration (minute)'),
                        tooltip=['year:O', 'mean(duration):Q']
                    ).properties(
                        width=200,
                        height=250
                    )

                    st.markdown('<p class="subtitle">Average Song Duration Across the Years</p>', unsafe_allow_html=True)
                    st.altair_chart(avg_duration_chart, use_container_width=True)

                # Add other graphs here as needed (danceability, number of songs per year, etc.)
                    st.markdown('<p class="subtitle">Most Popular Songs</p>', unsafe_allow_html=True)
                    most_popular_songs = artist_songs.sort_values(by='popularity', ascending=False).head(5)

                    # Create a bar chart for the top 5 most popular songs
                    popular_songs_chart = alt.Chart(most_popular_songs).mark_bar(color='#1DB954').encode(
                        x=alt.X('popularity:Q', title='Popularity'),
                        y=alt.Y('song:N', title='Song', sort='-x'),
                        tooltip=['song:N', 'popularity:Q']
                    ).properties(
                        width=200,
                        height=250
                    )

                    st.altair_chart(popular_songs_chart, use_container_width=True)

            #     st.altair_chart(songs_per_year_chart, use_container_width=True)
                # Donut chart for genres per song
                with col3:
                    st.markdown('<p class="subtitle">Genres per Song</p>', unsafe_allow_html=True)
                    # Explode genres for each song to handle multiple genres per song
                    genres_per_song = artist_songs.explode('genre')
                    genre_count = genres_per_song.groupby('genre')['song'].count().reset_index()
                    genre_count.columns = ['genre', 'num_songs']

                    # Create a donut chart for genres per song
                    # Create a donut chart for genres per song
                    donut_chart = alt.Chart(genre_count).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta('num_songs:Q', title='Number of Songs'),
                        color=alt.Color(
                            'genre:N',
                            scale=alt.Scale(scheme='greens'),  # Use green color scheme
                            legend=alt.Legend(title="Genre")
                        ),
                        tooltip=[
                            alt.Tooltip('genre:N', title='Genre'),
                            alt.Tooltip('num_songs:Q', title='Number of Songs', format='.0f')  # Ensure integer display
                        ]
                    ).properties(
                        width=150,
                        height=250
                    )
                    st.altair_chart(donut_chart, use_container_width=True)

                    # Loudness Distribution
                    st.markdown('<p class="subtitle">Loudness Distribution</p>', unsafe_allow_html=True)

                    loudness_distribution_chart = alt.Chart(artist_songs).mark_point(size=60, color='#1DB954').encode(
                        x=alt.X('song:N', title='Song', sort='-y'),  # Sort songs for better visibility
                        y=alt.Y('loudness:Q', title='Loudness (dB)'),
                        tooltip=[
                            alt.Tooltip('song:N', title='Song'),
                            alt.Tooltip('artist:N', title='Artist'),
                            alt.Tooltip('loudness:Q', title='Loudness (dB)', format='.2f')
                        ]
                    ).properties(
                        width=150,
                        height=250
                    )

                    st.altair_chart(loudness_distribution_chart, use_container_width=True)
        else:
            st.markdown("**No artists found.**")
    else:
        st.markdown("**Please enter an artist's name.**")

elif st.session_state.show_about:
    st.markdown('<p class="main-title">About</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="subtitle">
        Tugas Besar Visualisasi Data Kelompok 7 <br>
        <br>
        -	Muhammad Farhan Akmal (1301210486) <br>
        -	Sofi Nurhayati Latifah (1301210076) <br>
        -	Aisha Farizka Mawla (1301213122) <br>
        <br>
        Dashboard ini berfungsi untuk menganalisis data lagu Spotify. Anda dapat mencari lagu dan artis, 
        melihat informasi detail, dan menjelajahi berbagai statistik tentang tren dan popularitas musik. <br>
        <br>
        <strong>Deskripsi Dataset:</strong> <br>
        Dataset ini berisi lagu-lagu hits Spotify dari tahun 2000 hingga 2019, mencakup berbagai informasi seperti:
        <ul>
            <li><strong>Popularitas:</strong> Indikator seberapa populer sebuah lagu di platform Spotify.</li>
            <li><strong>Danceability:</strong> Ukuran seberapa cocok sebuah lagu untuk menari, dengan nilai antara 0.0 dan 1.0.</li>
            <li><strong>Energy:</strong> Ukuran intensitas dan aktivitas sebuah lagu, dari nilai 0.0 (tenang) hingga 1.0 (energetik).</li>
            <li><strong>Valence:</strong> Indikator mood lagu, dengan nilai mendekati 1.0 mewakili lagu yang ceria dan mendekati 0.0 mewakili lagu yang sedih.</li>
            <li><strong>Tempo:</strong> Kecepatan tempo lagu dalam BPM (beats per minute).</li>
            <li><strong>Genre:</strong> Informasi tentang kategori genre lagu.</li>
            <li><strong>Explicit:</strong> Indikator apakah sebuah lagu memiliki konten eksplisit.</li>
            <li><strong>Fitur Audio:</strong> Meliputi akustik, instrumental, dan lainnya.</li>
        <ul>
        <br>
        <strong>Sumber Dataset:</strong> Dataset ini berasal dari Kaggle
        <a href="https://www.kaggle.com/datasets/paradisejoy/top-hits-spotify-from-20002019" target="_blank">Top Hits Spotify from 2000-2019</a>.
    </p>
    """, unsafe_allow_html=True)
    st.dataframe(df)
    
else:
    st.markdown('<p class="main-title">Spotify Music Dataset Analysis Dashboard </p>', unsafe_allow_html=True)
    st.markdown('<p class="belowtitle">An interactive dashboard providing insights into Spotify\'s song and artist data from 1998 to 2020</p>', unsafe_allow_html=True)

    def make_donut(explicit_count, non_explicit_count, input_color):
        if input_color == 'green':
            chart_color = ['#E74C3C', '#1DB954']

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
            align='center', fontSize=30, fontWeight=600, color='#1DB954'
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
        genre_chart = alt.Chart(top_10_genres).mark_bar(color='#1DB954').encode(
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

        artist_chart = alt.Chart(top_artists_by_songs).mark_bar(color='#1DB954').encode(
            x=alt.X('song_count:Q', title='Number of Songs'),
            y=alt.Y('artist:N', sort='-x', title='Artist'),
            tooltip=['artist:N', 'song_count:Q']
        ).properties(
            width=400,
            height=280
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
        songs_trend_chart = alt.Chart(annual_trends).mark_line(color='#1DB954', point=True).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('total_songs:Q', title='Total Songs Released'),
            tooltip=['year:O', 'total_songs:Q']
        ).properties(
            width=400,
            height=280
        )
        st.altair_chart(songs_trend_chart, use_container_width=True)

    col1, col2 = st.columns((5, 5), gap='large')
    # Danceability Distribution Based on Songs
    with col1:
        st.markdown('<p class="subtitle">Top Genres by Popularity</p>', unsafe_allow_html=True)

        # Calculate the total popularity for each genre
        genre_popularity = (
            df.explode('genre')  # Handle multiple genres per song
            .groupby('genre')['popularity']
            .sum()
            .reset_index()
            .rename(columns={'popularity': 'total_popularity'})
        )

        # Sort genres by popularity and select the top 10
        top_genres = genre_popularity.sort_values(by='total_popularity', ascending=False).head(10)

        # Create a vertical bar chart for top genres by popularity
        top_genres_vertical_chart = alt.Chart(top_genres).mark_line(point=True, color='#1DB954').encode(
            x=alt.X('genre:N', title='Genre', sort='-y'),
            y=alt.Y('total_popularity:Q', title='Total Popularity'),
            tooltip=[
                alt.Tooltip('genre:N', title='Genre'),
                alt.Tooltip('total_popularity:Q', title='Total Popularity', format='.2f')
            ]
        ).properties(
            width=500,
            height=380
        )

        st.altair_chart(top_genres_vertical_chart, use_container_width=True)

    with col2:
        st.markdown('<p class="subtitle">Danceability Distribution by Genre</p>', unsafe_allow_html=True)

        # Prepare data: Flatten the genres for individual songs
        danceability_data = df.explode('genre')[['genre', 'danceability']]

        # Create a boxplot
        danceability_boxplot = alt.Chart(danceability_data).mark_boxplot(extent='min-max', color='#1DB954').encode(
            x=alt.X('danceability:Q', title='Danceability'),
            y=alt.Y('genre:N', title='Genre', sort='-x'),
            color=alt.Color('genre:N', legend=None),  # Use the default color for genres
            tooltip=[
                alt.Tooltip('genre:N', title='Genre'),
                alt.Tooltip('danceability:Q', title='Danceability')
            ]
        ).properties(
            width=500,
            height=380
        )

        st.altair_chart(danceability_boxplot, use_container_width=True)
