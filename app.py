import pickle
import streamlit as st
import requests
import gdown
import os

st.set_page_config(page_title="Movie Recommender", layout="wide")

# -------------------- DOWNLOAD FILE (ONLY ONCE) --------------------
@st.cache_resource
def download_similarity():
    if not os.path.exists("similarity.pkl"):
        url = "https://drive.google.com/uc?id=15n_cV5ahKfpJPB4hty9yBJ7opyOxUpFq"
        gdown.download(url, "similarity.pkl", quiet=False)

download_similarity()


# -------------------- SIMPLE CSS --------------------
st.markdown("""
<style>
.movie-text {
    white-space: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    max-width: 150px;
    font-weight: 500;
    margin-bottom: 5px;
}
img {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# -------------------- LOAD DATA --------------------
@st.cache_data
def load_movies():
    return pickle.load(open("movies.pkl", "rb"))

@st.cache_data
def load_similarity():
    return pickle.load(open("similarity.pkl", "rb"))

movies = load_movies()
similarity = load_similarity()


# -------------------- POSTER FETCH --------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        return "https://via.placeholder.com/300x450?text=No+API+Key"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        res = requests.get(url, timeout=4)

        if res.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Image"

        data = res.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w342" + data["poster_path"]
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=No+Image"


# -------------------- RECOMMEND FUNCTION --------------------
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except:
        return [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in distances:
        movie_id = movies.iloc[i[0]].id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


# -------------------- UI --------------------
st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox(
    "Select a movie",
    movies["title"].values
)


# -------------------- SHOW RECOMMENDATION --------------------
if st.button("Show Recommendation"):
    with st.spinner("Loading recommendations..."):
        names, posters = recommend(selected_movie)

    if len(names) == 0:
        st.error("Something went wrong. Try another movie.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)

        for col, i in zip([col1, col2, col3, col4, col5], range(5)):
            with col:
                st.markdown(
                    f"<div class='movie-text'>{names[i]}</div>",
                    unsafe_allow_html=True
                )
                st.image(posters[i], width=150)
