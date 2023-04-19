import streamlit as st
import pandas as pd
import requests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import plotly.graph_objects as go
# Set page config
st.set_page_config(page_title="Movie Recommendation System", page_icon=":clapper:")
# Set up the first tab
def first_tab():
    import requests
    # Define the API key
    api_key = "1a219482c51e5dc798ae1ac0a309d459"
    # Define the base URL for TMDb API requests
    BASE_URL = "https://api.themoviedb.org/3/{}?api_key=1a219482c51e5dc798ae1ac0a309d459&language=en-US"
    # Define the function to fetch movie information
    def fetch_movie_info(query):
        # Make API request to search for movie
        search_url = BASE_URL.format("search/movie") + "&query=" + query
        search_response = requests.get(search_url)
        search_data = search_response.json()
        # Check if there are any search results
        if "results" not in search_data or not search_data["results"]:
            st.write("TMDB Does not have the data of the movie you are searching for")
            return None
        # Get ID of first search result
        movie_id = search_data["results"][0]["id"]
        # Make API request to get movie info
        movie_url = BASE_URL.format("movie/" + str(movie_id))
        movie_response = requests.get(movie_url)
        movie_data = movie_response.json()
        # Extract relevant movie info
        movie_info = {
            "id": movie_data["id"],
            "name": movie_data["original_title"],
            "poster": "https://image.tmdb.org/t/p/w500" + movie_data["poster_path"],
            "title": movie_data["title"],
            "rating": round(movie_data["vote_average"], 1),
            "overview": movie_data["overview"]
        }
        return movie_info
    # Define the function to fetch related movies
    def fetch_related_movies(movie_id, num_recommendations=10):
        url = f"{BASE_URL.format('movie/' + str(movie_id) + '/recommendations')}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        movies = response.json()["results"][:num_recommendations]
        return [
            {
                "name": movie["original_title"],
                "poster": f"https://image.tmdb.org/t/p/w185{movie['poster_path']}",
                "title": movie["original_title"],
                "rating": round(movie["vote_average"], 1),
                "overview": movie["overview"]
            }
            for movie in movies
        ]
    # Define the UI layout
    st.title("Movie Recommendation System")
    # Define the search box
    search_query = st.text_input("Search for a movie")
    # If the search box is not empty, fetch and display the movie information
    if search_query:
        movie_info = fetch_movie_info(search_query)
        if movie_info is None:
            st.write("No results found. Please enter a valid movie name.")
        elif "status_message" in movie_info:
            st.write("The movie does not exist on TMDb server. Please enter a valid movie name.")
        else:
            # Create two columns for the image and movie information
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie_info["poster"])
            with col2:
                st.write("## " + movie_info["name"])
                st.write("**Title:** " + movie_info["title"])
                st.write("**Rating:** " + str(movie_info["rating"]))
                st.write("**Overview:** " + movie_info["overview"])
            # Fetch and display related movies
            st.header("Related Movies")
            # Fetch  related movies
            related_movies = fetch_related_movies(movie_info["id"])
            # Display the related movies
            for i, movie in enumerate(related_movies[:5]):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(movie["poster"], width=200)
                with col2:
                    st.write(f"## {i+1}. {movie['name']}")
                    st.write("**Title:** " + movie["title"])
                    st.write("**Rating:** " + str(movie["rating"]))
                    st.write("**Overview:** " + movie["overview"])
# Set up the third tab
def second_tab():
    import requests
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    # TMDB API URL and key
    tmdb_url = "https://api.themoviedb.org/3"
    tmdb_key = "1a219482c51e5dc798ae1ac0a309d459"
    # Function to search for a movie by name
    def search_movie(query):
        url = f"{tmdb_url}/search/movie?api_key={tmdb_key}&query={query}"
        response = requests.get(url)
        data = response.json()
        return data
    # Function to get movie details from TMDB API
    def get_movie_details(movie_id):
        url = f"{tmdb_url}/movie/{movie_id}?api_key={tmdb_key}&language=en-US"
        response = requests.get(url)
        data = response.json()
        return data
    # Function to get movie reviews from TMDB API
    def get_movie_reviews(movie_id):
        url = f"{tmdb_url}/movie/{movie_id}/reviews?api_key={tmdb_key}&language=en-US&page=1"
        response = requests.get(url)
        data = response.json()
        return data
    # Function to perform sentimental analysis using TextBlob
    def analyze_textblob(review):
        blob = TextBlob(review)
        sentiment = blob.sentiment.polarity
        if sentiment > 0:
            return "Positive"
        elif sentiment < 0:
            return "Negative"
        else:
            return "Neutral"
    # Function to perform sentimental analysis using Vader
    def analyze_vader(review):
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(review)
        compound = sentiment['compound']
        if compound > 0:
            return "Positive"
        elif compound < 0:
            return "Negative"
        else:
            return "Neutral"
    # Streamlit app
    def app():
        st.title("Sentimental Analysis of Movie Reviews")
        movie_name = st.text_input("Enter the movie name:", key="movie_name_input")
        if movie_name:
            # Search for movie by name
            search_results = search_movie(movie_name)
            if len(search_results["results"]) == 0:
                st.error("Movie not found. Please enter a valid movie name.")
                return
            # Get the first search result and extract movie ID
            movie_id = search_results["results"][0]["id"]
            # Get movie details from TMDB API
            movie_details = get_movie_details(movie_id)
            title = movie_details["title"]
            st.header(title)
            release_date = movie_details["release_date"]
            st.write(f"Release date: {release_date}")
            overview = movie_details["overview"]
            st.write(f"Overview: {overview}")
            # Get movie poster from TMDB API and display it
            poster_path = movie_details["poster_path"]
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                st.image(poster_url)
            else:
                st.warning("No poster found for this movie.")
            # Get movie reviews from TMDB API
            movie_reviews = get_movie_reviews(movie_id)
            if len(movie_reviews["results"]) == 0:
                st.warning("No reviews found for this movie.")
                return
            # Perform sentimental analysis using TextBlob and Vader
            textblob_sentiments = []
            vader_sentiments = []
            for review in movie_reviews["results"]:
                content = review["content"]
                # Perform sentimental analysis using TextBlob
                textblob_sentiments.append(analyze_textblob(content))
                # Perform sentimental analysis using Vader
                vader_sentiments.append(analyze_vader(content))
            # Generate visualization of sentiment analysis using Plotly
            import plotly.express as px
            import pandas as pd
            # Create dataframe with sentiment data
            data = {'Review': [review['content'] for review in movie_reviews["results"]],
                    'TextBlob': textblob_sentiments,
                    'Vader': vader_sentiments}
            df = pd.DataFrame(data)
            # Create bar chart
            fig = px.bar(df, x='Review', y=['TextBlob', 'Vader'], barmode='group', 
                        title=f"Sentiment Analysis of Reviews for '{title}'")
            st.plotly_chart(fig)
            # Create pie chart for sentiment distribution
            textblob_counts = df['TextBlob'].value_counts()
            vader_counts = df['Vader'].value_counts()
            fig = go.Figure(data=[go.Pie(labels=textblob_counts.index, values=textblob_counts.values, name="TextBlob"),
                                go.Pie(labels=vader_counts.index, values=vader_counts.values, name="Vader")])
            fig.update_traces(hole=.4, hoverinfo="label+percent+name")
            fig.update_layout(
                title={
                    'text': f"Sentiment Distribution for '{title}'",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'})
            st.plotly_chart(fig)
            # Create histogram for sentiment polarity distribution
            textblob_polarity = df['TextBlob'].apply(lambda x: TextBlob(x).sentiment.polarity)
            vader_polarity = df['Vader'].apply(lambda x: SentimentIntensityAnalyzer().polarity_scores(x)['compound'])
            fig = go.Figure(data=[go.Histogram(x=textblob_polarity, name="TextBlob", nbinsx=50),
                                go.Histogram(x=vader_polarity, name="Vader", nbinsx=50)])
            fig.update_layout(barmode='overlay')
            fig.update_traces(opacity=0.75)
            fig.update_layout(
                title={
                    'text': f"Sentiment Polarity Distribution for '{title}'",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                xaxis_title="Polarity",
                yaxis_title="Count")
            st.plotly_chart(fig)
    app()
# Create a dictionary of tabs
tabs = {
    "Movie Recommendation System": first_tab,
    "Sentimental Analysis": second_tab
}
# Create a function to run the selected tab
def run_tab():
    tab = st.sidebar.selectbox('Select a tab', options=list(tabs.keys()))
    tabs[tab]()
# Run the app
if __name__ == '__main__':
    run_tab()

