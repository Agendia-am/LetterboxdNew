"""
Letterboxd Data Visualization Report
Creates interactive charts from scraped Letterboxd data using Plotly
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import Counter
import pandas as pd
from pathlib import Path


def load_film_data(username):
    """Load scraped film data from JSON file"""
    filename = f'{username}_detailed_films.json'
    
    if not Path(filename).exists():
        print(f"Error: {filename} not found!")
        print("Please run the scraper first to generate the data.")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def prepare_dataframe(films):
    """Convert film data to pandas DataFrame for easier analysis"""
    df = pd.DataFrame(films)
    
    # Convert ratings to numeric
    df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce')
    df['personal_rating'] = pd.to_numeric(df['personal_rating'], errors='coerce')
    df['release_date'] = pd.to_numeric(df['release_date'], errors='coerce')
    
    # Extract runtime minutes
    df['runtime_mins'] = df['runtime'].apply(lambda x: 
        int(x.split()[0]) if isinstance(x, str) and 'min' in x else None
    )
    
    return df


def create_rating_distribution(df):
    """Create personal rating distribution histogram"""
    rated_films = df[df['personal_rating'].notna()]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=rated_films['personal_rating'],
        nbinsx=10,
        marker_color='#00c030',
        name='Personal Ratings'
    ))
    
    fig.update_layout(
        title='Personal Rating Distribution',
        xaxis_title='Rating (out of 5)',
        yaxis_title='Number of Films',
        template='plotly_dark',
        bargap=0.1
    )
    
    return fig


def create_rating_comparison(df):
    """Compare personal ratings vs average ratings"""
    rated_films = df[(df['personal_rating'].notna()) & (df['average_rating'].notna())]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rated_films['average_rating'],
        y=rated_films['personal_rating'],
        mode='markers',
        marker=dict(
            size=10,  # Increased from 8
            color=rated_films['personal_rating'],
            colorscale=[[0, '#ff0000'], [0.5, '#ffcc00'], [1, '#00e054']],  # Red to Yellow to Green
            showscale=True,
            colorbar=dict(
                title=dict(text="Your Rating", font=dict(size=14, color='white')),
                tickfont=dict(size=12, color='white')
            ),
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=rated_films['title'],
        hovertemplate='<b style="font-size:14px">%{text}</b><br>' +
                      '<b>Community:</b> %{x}/5<br>' +
                      '<b>Your Rating:</b> %{y}/5<extra></extra>',
        name='Films'
    ))
    
    # Add diagonal line (where personal = average)
    fig.add_trace(go.Scatter(
        x=[0, 5],
        y=[0, 5],
        mode='lines',
        line=dict(dash='dash', color='gray', width=3),
        name='Equal Rating Line',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=dict(
            text='Personal Rating vs Community Average',
            font=dict(size=20, color='white')
        ),
        xaxis_title=dict(text='Community Average Rating', font=dict(size=16, color='white')),
        yaxis_title=dict(text='Your Personal Rating', font=dict(size=16, color='white')),
        template='plotly_dark',
        xaxis=dict(range=[0, 5], tickfont=dict(size=14)),
        yaxis=dict(range=[0, 5], tickfont=dict(size=14)),
        height=700,
        hoverlabel=dict(bgcolor="rgba(0,0,0,0.9)", font=dict(size=14)),
        legend=dict(font=dict(size=14))
    )
    
    return fig


def create_films_by_year(df):
    """Create bar chart of films watched by release year"""
    year_counts = df['release_date'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=year_counts.index,
        y=year_counts.values,
        marker_color='#ff8000',
        name='Films'
    ))
    
    fig.update_layout(
        title='Films by Release Year',
        xaxis_title='Year',
        yaxis_title='Number of Films',
        template='plotly_dark',
        bargap=0.1
    )
    
    return fig


def create_top_genres(df, top_n=15):
    """Create bar chart of top genres"""
    # Flatten genres list
    all_genres = []
    for genres in df['genres']:
        if isinstance(genres, list):
            all_genres.extend(genres)
    
    genre_counts = Counter(all_genres).most_common(top_n)
    genres, counts = zip(*genre_counts) if genre_counts else ([], [])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(counts),
        y=list(genres),
        orientation='h',
        marker_color='#40bcf4',
        name='Films'
    ))
    
    fig.update_layout(
        title=f'Top {top_n} Genres',
        xaxis_title='Number of Films',
        yaxis_title='Genre',
        template='plotly_dark',
        height=500
    )
    
    return fig


def create_top_directors(df, top_n=20):
    """Create bar chart of top directors"""
    all_directors = []
    for directors in df['directors']:
        if isinstance(directors, list):
            all_directors.extend(directors)
    
    director_counts = Counter(all_directors).most_common(top_n)
    directors, counts = zip(*director_counts) if director_counts else ([], [])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(counts),
        y=list(directors),
        orientation='h',
        marker_color='#00e054',
        name='Films'
    ))
    
    fig.update_layout(
        title=f'Top {top_n} Directors',
        xaxis_title='Number of Films',
        yaxis_title='Director',
        template='plotly_dark',
        height=600
    )
    
    return fig


def create_runtime_distribution(df):
    """Create histogram of film runtimes"""
    runtime_data = df[df['runtime_mins'].notna()]['runtime_mins']
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=runtime_data,
        nbinsx=30,
        marker_color='#9c27b0',
        name='Films'
    ))
    
    fig.update_layout(
        title='Runtime Distribution',
        xaxis_title='Runtime (minutes)',
        yaxis_title='Number of Films',
        template='plotly_dark',
        bargap=0.1
    )
    
    return fig


def create_rating_by_decade(df):
    """Create box plot of ratings by decade"""
    rated_films = df[(df['personal_rating'].notna()) & (df['release_date'].notna())]
    rated_films['decade'] = (rated_films['release_date'] // 10) * 10
    
    decades = sorted(rated_films['decade'].unique())
    
    fig = go.Figure()
    
    for decade in decades:
        decade_data = rated_films[rated_films['decade'] == decade]['personal_rating']
        fig.add_trace(go.Box(
            y=decade_data,
            name=f"{int(decade)}s",
            marker_color='#ff6b6b'
        ))
    
    fig.update_layout(
        title='Personal Ratings by Decade',
        xaxis_title='Decade',
        yaxis_title='Personal Rating',
        template='plotly_dark',
        showlegend=False
    )
    
    return fig


def create_top_actors(df, top_n=30):
    """Create bar chart of top actors"""
    all_actors = []
    for actors in df['actors']:
        if isinstance(actors, list):
            all_actors.extend(actors)
    
    actor_counts = Counter(all_actors).most_common(top_n)
    actors, counts = zip(*actor_counts) if actor_counts else ([], [])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(counts),
        y=list(actors),
        orientation='h',
        marker_color='#ffd700',
        name='Films'
    ))
    
    fig.update_layout(
        title=f'Top {top_n} Actors',
        xaxis_title='Number of Films',
        yaxis_title='Actor',
        template='plotly_dark',
        height=900
    )
    
    return fig


def create_genre_rating_heatmap(df):
    """Create heatmap of average personal ratings by genre - ALL genres"""
    genre_ratings = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['personal_rating']) and isinstance(film['genres'], list):
            for genre in film['genres']:
                if genre not in genre_ratings:
                    genre_ratings[genre] = []
                genre_ratings[genre].append(film['personal_rating'])
    
    # Calculate average rating per genre (show all with at least 1 film)
    genre_avg = {genre: sum(ratings)/len(ratings) 
                 for genre, ratings in genre_ratings.items()}
    
    # Sort by average rating
    sorted_genres = sorted(genre_avg.items(), key=lambda x: x[1], reverse=True)
    genres, avgs = zip(*sorted_genres) if sorted_genres else ([], [])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(avgs),
        y=list(genres),
        orientation='h',
        marker=dict(
            color=list(avgs),
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Avg Rating")
        ),
        text=[f"{avg:.2f}" for avg in avgs],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Average Personal Rating by Genre',
        xaxis_title='Average Rating',
        yaxis_title='Genre',
        template='plotly_dark',
        height=600,
        xaxis=dict(range=[0, 5])
    )
    
    return fig


def create_countries_map(df):
    """Create choropleth map showing countries where movies were watched from"""
    all_countries = []
    for countries in df['country']:
        if isinstance(countries, list):
            all_countries.extend(countries)
    
    country_counts = Counter(all_countries)
    
    # Map country names to ISO codes (common ones)
    country_code_map = {
        'USA': 'USA', 'United States': 'USA', 'United Kingdom': 'GBR', 'UK': 'GBR',
        'France': 'FRA', 'Germany': 'DEU', 'Italy': 'ITA', 'Spain': 'ESP',
        'Japan': 'JPN', 'South Korea': 'KOR', 'China': 'CHN', 'India': 'IND',
        'Canada': 'CAN', 'Australia': 'AUS', 'Brazil': 'BRA', 'Mexico': 'MEX',
        'Russia': 'RUS', 'Sweden': 'SWE', 'Norway': 'NOR', 'Denmark': 'DNK',
        'Netherlands': 'NLD', 'Belgium': 'BEL', 'Poland': 'POL', 'Argentina': 'ARG',
        'Hong Kong': 'HKG', 'Taiwan': 'TWN', 'New Zealand': 'NZL', 'Ireland': 'IRL',
        'Austria': 'AUT', 'Switzerland': 'CHE', 'Czech Republic': 'CZE', 'Finland': 'FIN',
        'Greece': 'GRC', 'Portugal': 'PRT', 'Turkey': 'TUR', 'Israel': 'ISR'
    }
    
    countries_mapped = []
    counts_mapped = []
    for country, count in country_counts.items():
        if country in country_code_map:
            countries_mapped.append(country_code_map[country])
            counts_mapped.append(count)
    
    fig = go.Figure(data=go.Choropleth(
        locations=countries_mapped,
        z=counts_mapped,
        locationmode='ISO-3',
        colorscale='Reds',
        colorbar_title='Films',
        marker_line_color='darkgray',
        marker_line_width=0.5,
    ))
    
    fig.update_layout(
        title='Films by Country (Geographic Distribution)',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)'
        ),
        template='plotly_dark',
        height=600
    )
    
    return fig


def create_rating_by_year(df):
    """Compare personal vs average rating for every year using area chart"""
    rated_films = df[(df['personal_rating'].notna()) & 
                     (df['average_rating'].notna()) & 
                     (df['release_date'].notna())]
    
    # Group by year - show ALL years
    year_stats = rated_films.groupby('release_date').agg({
        'personal_rating': 'mean',
        'average_rating': 'mean',
        'title': 'count'
    }).reset_index()
    
    year_stats = year_stats.sort_values('release_date')
    
    fig = go.Figure()
    
    # Area chart for personal rating
    fig.add_trace(go.Scatter(
        x=year_stats['release_date'],
        y=year_stats['personal_rating'],
        fill='tozeroy',
        mode='lines',
        name='Your Average Rating',
        line=dict(color='#00e054', width=2),
        fillcolor='rgba(0, 224, 84, 0.3)'
    ))
    
    # Area chart for community rating
    fig.add_trace(go.Scatter(
        x=year_stats['release_date'],
        y=year_stats['average_rating'],
        fill='tozeroy',
        mode='lines',
        name='Community Average Rating',
        line=dict(color='#40bcf4', width=2),
        fillcolor='rgba(64, 188, 244, 0.3)'
    ))
    
    fig.update_layout(
        title='Personal vs Community Rating by Year (Area Chart)',
        xaxis_title='Year',
        yaxis_title='Average Rating',
        template='plotly_dark',
        hovermode='x unified',
        yaxis=dict(range=[0, 5]),
        height=600
    )
    
    return fig


def create_studio_ratings(df):
    """Compare studio average ratings using treemap - ALL studios"""
    studio_data = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['personal_rating']) and isinstance(film['studios'], list):
            for studio in film['studios']:
                if studio not in studio_data:
                    studio_data[studio] = {'ratings': [], 'count': 0}
                studio_data[studio]['ratings'].append(film['personal_rating'])
                studio_data[studio]['count'] += 1
    
    # Show ALL studios
    studios = []
    ratings = []
    counts = []
    labels = []
    
    for studio, data in studio_data.items():
        avg_rating = sum(data['ratings']) / len(data['ratings'])
        studios.append(studio)
        ratings.append(avg_rating)
        counts.append(data['count'])
        labels.append(f"{studio}<br>{avg_rating:.2f}★ ({data['count']} films)")
    
    if not studios:
        return go.Figure()
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[''] * len(studios),
        values=counts,
        marker=dict(
            colors=ratings,
            colorscale='RdYlGn',
            cmid=2.5,
            colorbar=dict(title="Avg Rating"),
            line=dict(width=2)
        ),
        textposition='middle center',
        hovertemplate='<b>%{label}</b><extra></extra>'
    ))
    
    fig.update_layout(
        title='All Studios by Film Count and Rating (Treemap)',
        template='plotly_dark',
        height=700
    )
    
    return fig


def create_director_actor_collaboration(df):
    """Director-actor collaborations using Sankey diagram - ALL collaborations"""
    collaborations = {}
    
    for _, film in df.iterrows():
        if isinstance(film['directors'], list) and isinstance(film['actors'], list):
            for director in film['directors']:
                for actor in film['actors']:
                    pair = (director, actor)
                    if pair not in collaborations:
                        collaborations[pair] = 0
                    collaborations[pair] += 1
    
    # Show all collaborations, sorted by count (limit to top 50 for readability)
    filtered_collabs = [(d, a, count) for (d, a), count in collaborations.items()]
    filtered_collabs = sorted(filtered_collabs, key=lambda x: x[2], reverse=True)[:50]
    
    if not filtered_collabs:
        return go.Figure()
    
    # Build Sankey diagram
    directors = list(set([d for d, _, _ in filtered_collabs]))
    actors = list(set([a for _, a, _ in filtered_collabs]))
    
    # Create labels and indices
    all_labels = directors + actors
    label_to_idx = {label: idx for idx, label in enumerate(all_labels)}
    
    source = [label_to_idx[d] for d, _, _ in filtered_collabs]
    target = [label_to_idx[a] for _, a, _ in filtered_collabs]
    values = [count for _, _, count in filtered_collabs]
    
    # Color by value
    link_colors = [f'rgba(255, 105, 180, {0.2 + 0.6 * (v / max(values))})' for v in values]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=all_labels,
            color='#ff69b4'
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=link_colors
        )
    )])
    
    fig.update_layout(
        title='Top 50 Director-Actor Collaboration Network (Sankey)',
        template='plotly_dark',
        height=800,
        font=dict(size=10)
    )
    
    return fig


def create_genre_personal_rating_scatter(df):
    """Personal rating comparison across genres using radar chart - ALL genres"""
    genre_ratings = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['personal_rating']) and isinstance(film['genres'], list):
            for genre in film['genres']:
                if genre not in genre_ratings:
                    genre_ratings[genre] = []
                genre_ratings[genre].append(film['personal_rating'])
    
    # Calculate average and count for ALL genres
    genre_stats = {genre: {
        'avg': sum(ratings) / len(ratings),
        'count': len(ratings)
    } for genre, ratings in genre_ratings.items()}
    
    if not genre_stats:
        return go.Figure()
    
    # Sort by count and take top genres for readability
    sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
    
    genres = [g for g, _ in sorted_genres]
    avg_ratings = [stats['avg'] for _, stats in sorted_genres]
    counts = [stats['count'] for _, stats in sorted_genres]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=avg_ratings,
        theta=genres,
        fill='toself',
        name='Average Rating',
        line=dict(color='#00e054', width=3),
        fillcolor='rgba(0, 224, 84, 0.4)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickfont=dict(size=14, color='white')
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='white')
            )
        ),
        showlegend=False,
        title=dict(
            text='Top 15 Genre Ratings (Radar Chart)',
            font=dict(size=20, color='white')
        ),
        template='plotly_dark',
        height=800
    )
    
    return fig


def create_runtime_by_genre(df):
    """Compare runtime to genre using treemap"""
    genre_data = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['runtime_mins']) and isinstance(film['genres'], list):
            for genre in film['genres']:
                if genre not in genre_data:
                    genre_data[genre] = {'runtimes': [], 'count': 0}
                genre_data[genre]['runtimes'].append(film['runtime_mins'])
                genre_data[genre]['count'] += 1
    
    if not genre_data:
        return go.Figure()
    
    genres = []
    avg_runtimes = []
    counts = []
    labels = []
    
    for genre, data in genre_data.items():
        avg_runtime = sum(data['runtimes']) / len(data['runtimes'])
        genres.append(genre)
        avg_runtimes.append(avg_runtime)
        counts.append(data['count'])
        labels.append(f"{genre}<br>{avg_runtime:.0f} min<br>({data['count']} films)")
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[''] * len(genres),
        values=counts,
        marker=dict(
            colors=avg_runtimes,
            colorscale='Viridis',
            colorbar=dict(title="Avg Runtime (min)"),
            line=dict(width=2)
        ),
        textposition='middle center',
        hovertemplate='<b>%{label}</b><extra></extra>'
    ))
    
    fig.update_layout(
        title='Genre Runtime Treemap (size=count, color=avg runtime)',
        template='plotly_dark',
        height=700
    )
    
    return fig


def create_actor_rating_count(df):
    """Compare actor personal rating and count of films seen - Treemap"""
    actor_ratings = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['personal_rating']) and isinstance(film['actors'], list):
            for actor in film['actors']:
                if actor not in actor_ratings:
                    actor_ratings[actor] = []
                actor_ratings[actor].append(film['personal_rating'])
    
    # Show top 50 actors by count
    actor_stats = []
    for actor, ratings in actor_ratings.items():
        actor_stats.append({
            'actor': actor,
            'avg_rating': sum(ratings) / len(ratings),
            'count': len(ratings)
        })
    
    if not actor_stats:
        return go.Figure()
    
    actor_df = pd.DataFrame(actor_stats).sort_values('count', ascending=False).head(50)
    
    # Create treemap with size=count, color=rating
    fig = go.Figure(go.Treemap(
        labels=actor_df['actor'],
        parents=[''] * len(actor_df),
        values=actor_df['count'],
        marker=dict(
            colorscale=[[0, '#ff0000'], [0.5, '#8b00ff'], [1, '#0066ff']],  # Red to Purple to Blue
            cmid=2.5,
            colorbar=dict(
                title=dict(text="Avg<br>Rating", font=dict(size=14, color='white')),
                tickfont=dict(size=12, color='white')
            ),
            line=dict(width=3, color='white')
        ),
        marker_colorscale=[[0, '#ff0000'], [0.5, '#8b00ff'], [1, '#0066ff']],
        marker_colors=actor_df['avg_rating'],
        text=actor_df['actor'],
        textfont=dict(size=16, color='white', family='Arial Black'),
        hovertemplate='<b style="font-size:16px">%{label}</b><br>' +
                      '<b>Films Watched:</b> %{value}<br>' +
                      '<b>Avg Rating:</b> %{color:.2f}/5<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 50 Actors: Films Watched (size) vs Rating (color)',
            font=dict(size=20, color='white')
        ),
        template='plotly_dark',
        height=900,
        hoverlabel=dict(bgcolor="rgba(0,0,0,0.9)", font=dict(size=14))
    )
    
    return fig


def create_language_distribution(df):
    """Compare amount of films from each language using sunburst chart"""
    language_counts = df['language'].value_counts()
    
    # Group smaller languages into "Other" - show top 25
    top_languages = language_counts.head(25)
    other_count = language_counts[25:].sum() if len(language_counts) > 25 else 0
    
    labels = ['All Languages'] + list(top_languages.index)
    parents = [''] + ['All Languages'] * len(top_languages)
    values = [top_languages.sum()] + list(top_languages.values)
    
    if other_count > 0:
        labels.append('Other Languages')
        parents.append('All Languages')
        values.append(other_count)
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        marker=dict(
            colorscale='Sunset',
            line=dict(width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Films: %{value}<br>Percentage: %{percentParent}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Films by Language (Sunburst Chart)',
        template='plotly_dark',
        height=700
    )
    
    return fig


def create_composer_actor_rating(df):
    """Compare composer and actor collaboration with average rating - ALL collaborations"""
    collaborations = {}
    
    for _, film in df.iterrows():
        if pd.notna(film['composer']) and isinstance(film['actors'], list) and pd.notna(film['personal_rating']):
            composer = film['composer']
            for actor in film['actors']:
                pair = f"{composer} (composer) + {actor}"
                if pair not in collaborations:
                    collaborations[pair] = []
                collaborations[pair].append(film['personal_rating'])
    
    # Calculate average rating for ALL collaborations (top 30 for readability)
    collab_ratings = {pair: {
        'avg_rating': sum(ratings) / len(ratings),
        'count': len(ratings)
    } for pair, ratings in collaborations.items()}
    
    sorted_collabs = sorted(collab_ratings.items(), 
                           key=lambda x: (x[1]['count'], x[1]['avg_rating']), 
                           reverse=True)[:30]
    
    if not sorted_collabs:
        return go.Figure()
    
    pairs = [pair for pair, _ in sorted_collabs]
    ratings = [data['avg_rating'] for _, data in sorted_collabs]
    counts = [data['count'] for _, data in sorted_collabs]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ratings,
        y=pairs,
        orientation='h',
        marker=dict(
            color=ratings,
            colorscale='Rainbow',
            showscale=True,
            colorbar=dict(title="Avg Rating")
        ),
        text=[f"{rating:.2f} ({count} films)" for rating, count in zip(ratings, counts)],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Top 30 Composer-Actor Collaborations by Rating',
        xaxis_title='Average Personal Rating',
        yaxis_title='Composer + Actor',
        template='plotly_dark',
        height=900,
        xaxis=dict(range=[0, 5])
    )
    
    return fig


def create_summary_stats(df):
    """Create a summary statistics figure"""
    total_films = len(df)
    rated_films = df['personal_rating'].notna().sum()
    avg_personal = df['personal_rating'].mean()
    avg_community = df['average_rating'].mean()
    total_runtime = df['runtime_mins'].sum() / 60  # Convert to hours
    
    stats_text = f"""
    <b style='font-size:24px'>Total Films:</b> <span style='font-size:24px; color:#00e054'>{total_films}</span><br><br>
    <b style='font-size:24px'>Films You've Rated:</b> <span style='font-size:24px; color:#40bcf4'>{rated_films}</span><br><br>
    <b style='font-size:24px'>Your Average Rating:</b> <span style='font-size:24px; color:#ffcc00'>{avg_personal:.2f}/5</span><br><br>
    <b style='font-size:24px'>Community Average:</b> <span style='font-size:24px; color:#ff8000'>{avg_community:.2f}/5</span><br><br>
    <b style='font-size:24px'>Total Watch Time:</b> <span style='font-size:24px; color:#9c27b0'>{total_runtime:.1f} hours</span><br>
    """
    
    fig = go.Figure()
    fig.add_annotation(
        text=stats_text,
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        font=dict(size=20, color="white"),
        align="left"
    )
    
    fig.update_layout(
        title=dict(
            text='Summary Statistics',
            font=dict(size=24, color='white')
        ),
        template='plotly_dark',
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig


def generate_report(username, recommendations=None):
    """Generate complete visualization report with optional recommendations"""
    print(f"Loading data for {username}...")
    films = load_film_data(username)
    
    if not films:
        return
    
    print(f"Loaded {len(films)} films")
    print("Preparing data...")
    df = prepare_dataframe(films)
    
    print("Creating visualizations...")
    
    # Create all charts
    charts = {
        'summary': create_summary_stats(df),
        'rating_dist': create_rating_distribution(df),
        'rating_comparison': create_rating_comparison(df),
        'films_by_year': create_films_by_year(df),
        'top_genres': create_top_genres(df),
        'top_directors': create_top_directors(df),
        'runtime_dist': create_runtime_distribution(df),
        'rating_by_decade': create_rating_by_decade(df),
        'top_actors': create_top_actors(df),
        'genre_ratings': create_genre_rating_heatmap(df),
        # New charts
        'countries': create_countries_map(df),
        'rating_by_year': create_rating_by_year(df),
        'studio_ratings': create_studio_ratings(df),
        'director_actor_collab': create_director_actor_collaboration(df),
        'genre_rating_scatter': create_genre_personal_rating_scatter(df),
        'runtime_by_genre': create_runtime_by_genre(df),
        'actor_rating_count': create_actor_rating_count(df),
        'language_dist': create_language_distribution(df),
        'composer_actor_rating': create_composer_actor_rating(df)
    }
    
    # Save individual charts
    output_dir = Path('visualizations')
    output_dir.mkdir(exist_ok=True)
    
    for name, fig in charts.items():
        output_file = output_dir / f'{username}_{name}.html'
        fig.write_html(str(output_file))
        print(f"✓ Saved {name} to {output_file}")
    
    # Create combined dashboard
    print("\nCreating combined dashboard...")
    
    # Create HTML report with all charts
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Letterboxd Report - {username}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #14181c;
                color: white;
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                text-align: center;
                color: #00e054;
            }}
            h2 {{
                color: #00e054;
                text-align: center;
                margin-top: 40px;
            }}
            .chart-container {{
                margin: 20px auto;
                max-width: 1200px;
            }}
            iframe {{
                width: 100%;
                border: none;
            }}
            .recommendations {{
                max-width: 1200px;
                margin: 40px auto;
                padding: 30px;
                background-color: #1c2228;
                border-radius: 10px;
                border: 2px solid #00e054;
            }}
            .recommendation {{
                background-color: #2c3440;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #00e054;
            }}
            .recommendation h3 {{
                margin-top: 0;
                color: #00e054;
                font-size: 1.3em;
            }}
            .recommendation .info {{
                margin: 10px 0;
                color: #9ab;
            }}
            .recommendation .rating {{
                color: #ff8000;
                font-weight: bold;
            }}
            .recommendation .genres {{
                color: #678;
                font-style: italic;
            }}
            .recommendation .reason {{
                color: #abc;
                margin: 8px 0;
                padding-left: 15px;
                border-left: 2px solid #456;
            }}
            .recommendation a {{
                color: #00e054;
                text-decoration: none;
                display: inline-block;
                margin-top: 10px;
            }}
            .recommendation a:hover {{
                text-decoration: underline;
            }}
            .no-recommendations {{
                text-align: center;
                color: #9ab;
                padding: 30px;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Letterboxd Visualization Report: {username}</h1>
    """
    
    # Add recommendations section if available
    if recommendations and len(recommendations) > 0:
        html_content += """
        <div class="recommendations">
            <h2>🎬 Recommended Movies for You</h2>
            <p style="text-align: center; color: #9ab;">Based on your viewing history and preferences</p>
        """
        
        for rec in recommendations:
            title = rec.get('title', 'Unknown')
            year = rec.get('year', 'N/A')
            # Format year as integer (no decimals)
            if year != 'N/A':
                try:
                    year = int(float(year))
                except (ValueError, TypeError):
                    year = 'N/A'
            rating = rec.get('average_rating', 'N/A')
            genres = rec.get('genres', [])
            directors = rec.get('directors', [])
            reasons = rec.get('reasons', [])
            url = rec.get('url', '#')
            rank = rec.get('rank', '?')
            
            genres_str = ', '.join(genres[:3]) if genres else 'N/A'
            directors_str = ', '.join(directors[:2]) if directors else 'N/A'
            
            html_content += f"""
            <div class="recommendation">
                <h3>{rank}. {title} ({year})</h3>
                <div class="info">
                    <span class="rating">⭐ {rating}/5</span> • 
                    <span class="genres">🎭 {genres_str}</span>
                </div>
                <div class="info">🎬 Director: {directors_str}</div>
            """
            
            if reasons:
                html_content += '<div style="margin-top: 15px;">'
                for reason in reasons[:3]:
                    html_content += f'<div class="reason">💡 {reason}</div>'
                html_content += '</div>'
            
            html_content += f"""
                <a href="{url}" target="_blank">View on Letterboxd →</a>
            </div>
            """
        
        html_content += """
        </div>
        """
    
    for name, fig in charts.items():
        height = fig.layout.height if fig.layout.height else 500
        html_content += f"""
        <div class="chart-container">
            <iframe src="{username}_{name}.html" height="{height + 100}"></iframe>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    dashboard_file = output_dir / f'{username}_dashboard.html'
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n{'='*60}")
    print(f"✓ Complete dashboard saved to: {dashboard_file}")
    print(f"{'='*60}")
    print(f"\nOpen the dashboard in your browser to view all visualizations!")
    
    return dashboard_file


def main():
    """Main function"""
    username = input("Enter Letterboxd username: ").strip()
    
    if not username:
        print("Error: Username cannot be empty!")
        return
    
    dashboard_file = generate_report(username)
    
    if dashboard_file:
        # Try to open in browser
        import webbrowser
        try:
            webbrowser.open(f'file://{dashboard_file.absolute()}')
            print("\nOpening dashboard in browser...")
        except Exception as e:
            print(f"\nCouldn't auto-open browser: {e}")
            print(f"Manually open: {dashboard_file.absolute()}")


if __name__ == "__main__":
    main()
