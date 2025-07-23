
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px



st.title("🎬 Netflix Content Analysis Dashboard")

st.markdown("""
<div style='text-align: center;'>
    <img src='https://plus.unsplash.com/premium_photo-1710961232986-36cead00da3c?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bW92aWVzfGVufDB8fDB8fHww' width='500' height='500'>
    <p style='font-size: 14px;'>Netflix Vibes</p>
</div>
""", unsafe_allow_html=True)



st.markdown("""
<style>
.big-font {
    font-size:32px !important;
    color: #e50914;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📺 Netflix Dashboard – Data Storytelling Edition</p>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    df['duration'] = df['duration'].fillna("Unknown")
    df['country'] = df['country'].fillna("Unknown")
    df['listed_in'] = df['listed_in'].fillna("Unknown")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
types = st.sidebar.multiselect("Select Type", df['type'].unique(), default=df['type'].unique())
years = st.sidebar.slider("Release Year", int(df['release_year'].min()), int(df['release_year'].max()), (2010, 2020))
countries = st.sidebar.multiselect("Select Country", df['country'].value_counts().head(20).index, default=None)

filtered_df = df[df['type'].isin(types)]
filtered_df = filtered_df[(filtered_df['release_year'] >= years[0]) & (filtered_df['release_year'] <= years[1])]
if countries:
    filtered_df = filtered_df[filtered_df['country'].isin(countries)]

# Key insights
with st.expander("📌 Key Insights Summary"):
    st.markdown("""
    - 📈 Netflix saw a major spike in content addition around **2018–2019**
    - 🎭 **Dramas**, **Comedies**, and **Documentaries** dominate the genre pool
    - 🌍 Most content comes from **United States**, followed by **India** and **United Kingdom**
    - 🎬 Movies still outnumber TV Shows, but shows are growing
    """)

# Titles by type
st.subheader("📊 Number of Titles by Type")
type_count = filtered_df['type'].value_counts()
st.bar_chart(type_count)

# Titles Added Over Years (Fixed)
st.subheader("📅 Titles Added Over the Years")
yearwise = filtered_df['year_added'].value_counts().sort_index()
yearwise = yearwise[yearwise.index.notnull()]
yearwise.index = yearwise.index.astype(int)
fig1, ax1 = plt.subplots()
ax1.plot(yearwise.index, yearwise.values, marker='o', linestyle='-', color='skyblue')
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of Titles")
ax1.set_title("Titles Added to Netflix Over the Years")
ax1.grid(True)
st.pyplot(fig1)

# Monthly Trend of Titles Added
st.subheader("📈 Monthly Trend of Titles Added")
monthly_trend = filtered_df.dropna(subset=['date_added']).copy()
monthly_trend['Month-Year'] = monthly_trend['date_added'].dt.to_period('M').astype(str)
monthly_data = monthly_trend.groupby('Month-Year').size().reset_index(name='count')
fig2 = px.line(monthly_data, x='Month-Year', y='count', title="Monthly Content Added Trend", markers=True)
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# Top Genres
st.subheader("🎭 Top 10 Genres")
genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10)
fig3, ax3 = plt.subplots()
sns.barplot(x=genres.values, y=genres.index, palette="magma", ax=ax3)
ax3.set_xlabel("Count")
ax3.set_ylabel("Genre")
st.pyplot(fig3)

# Genre-wise by type
st.subheader("🎞️ Genre-wise Content by Type (Movies vs TV Shows)")
genre_df = filtered_df.copy()
genre_df = genre_df.assign(genre=genre_df['listed_in'].str.split(', ')).explode('genre')
genre_plot = genre_df.groupby(['type', 'genre']).size().reset_index(name='count')
top_genres = genre_plot.groupby('genre')['count'].sum().nlargest(10).index
genre_plot = genre_plot[genre_plot['genre'].isin(top_genres)]
fig4 = px.bar(genre_plot, x='genre', y='count', color='type', barmode='group', title="Top Genres by Content Type")
st.plotly_chart(fig4, use_container_width=True)

# Country analysis
st.subheader("🌍 Top 10 Countries by Titles")
top_countries = filtered_df['country'].value_counts().head(10)
fig5, ax5 = plt.subplots()
sns.barplot(x=top_countries.values, y=top_countries.index, palette="viridis", ax=ax5)
ax5.set_xlabel("Number of Titles")
st.pyplot(fig5)

# Ratings
# Remove duration-like ratings (e.g., "74 min", "90 min")
cleaned_ratings = filtered_df[~filtered_df['rating'].str.contains(r'^\d+\s*min$', na=False)]

# Now count valid ratings
rating_counts = cleaned_ratings['rating'].value_counts()
st.subheader("📺 Content Ratings")
fig6, ax_bar = plt.subplots()
sns.barplot(x=rating_counts.values, y=rating_counts.index, palette="plasma", ax=ax_bar)
ax_bar.set_xlabel("Count")
ax_bar.set_ylabel("Rating")
st.pyplot(fig6)

# Top directors and actors
st.subheader("📊 Top 10 Global Insights")

tab1, tab2, tab3 = st.tabs(["🎬 Directors", "⭐ Actors", "🌍 Countries"])

with tab1:
    if 'director' in df.columns:
        top_directors = (
            df['director'].dropna().str.split(', ')
            .explode().value_counts().head(10)
        )
        fig_directors, ax = plt.subplots()
        sns.barplot(x=top_directors.values, y=top_directors.index, palette="magma", ax=ax)
        ax.set_title("Top 10 Directors", fontsize=14)
        ax.set_xlabel("Number of Titles")
        st.pyplot(fig_directors)
    else:
        st.warning("No 'director' column found in data.")

with tab2:
    if 'cast' in df.columns:
        top_actors = (
            df['cast'].dropna().str.split(', ')
            .explode().value_counts().head(10)
        )
        fig_actors, ax = plt.subplots()
        sns.barplot(x=top_actors.values, y=top_actors.index, palette="plasma", ax=ax)
        ax.set_title("Top 10 Actors", fontsize=14)
        ax.set_xlabel("Number of Titles")
        st.pyplot(fig_actors)
    else:
        st.warning("No 'cast' column found in data.")

with tab3:
    if 'country' in df.columns:
        top_countries = (
            df['country'].dropna().str.split(', ')
            .explode().value_counts().head(10)
        )
        fig_countries, ax = plt.subplots()
        sns.barplot(x=top_countries.values, y=top_countries.index, palette="viridis", ax=ax)
        ax.set_title("Top 10 Countries", fontsize=14)
        ax.set_xlabel("Number of Titles")
        st.pyplot(fig_countries)
    else:
        st.warning("No 'country' column found in data.")



# Search title
st.subheader("🔍 Search by Title")
search2_term = st.text_input("Enter part of a title to search:")

if search2_term:
    results = filtered_df[filtered_df['title'].str.contains(search2_term, case=False, na=False)]
    st.write(f"Found {len(results)} result(s)")

    if not results.empty:
        for i in range(0, min(9, len(results)), 3):  # 3 cards per row
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(results):
                    row = results.iloc[i + j]
                    title = row['title']
                    imdb_link = f"https://www.imdb.com/find?q={title.replace(' ', '+')}"
                    yt_link = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+trailer"

                    with cols[j]:
                        st.markdown(f"""
                        <div style='
                            border:1px solid #444;
                            border-radius:10px;
                            padding:15px;
                            margin-bottom:15px;
                            background-color:#f0f0f0;
                            color:#111;
                            height: 300px;
                            overflow-y: auto;
                            box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
                        '>
                            <h4 style='margin-bottom:10px;'>{title.title()}</h4>
                            <div style='font-size: 14px; line-height: 1.5;'>
                                <p><b>Type:</b> {row['type']}</p>
                                <p><b>Genre:</b> {row['listed_in']}</p>
                                <p><b>Release Year:</b> {row['release_year']}</p>
                                <p><b>Rating:</b> {row['rating']}</p>
                                <p><b>Country:</b> {row['country']}</p>
                                <a href="{imdb_link}" target="_blank">🔎 IMDb</a> |
                                <a href="{yt_link}" target="_blank">🎬 Trailer</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.warning("No matching titles found.")





# Preview and Download
st.subheader("🗃️ Filtered Dataset")
st.dataframe(filtered_df.head(20))
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered CSV", csv, "filtered_netflix_data.csv", "text/csv")
