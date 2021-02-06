import sys
import os
import pandas as pd
import pickle
import numpy as np
import streamlit as st

from backend.chunker import Chunker
from backend.recommender import Recommender
from backend.utils import save_to_cache


def create_database(file: str, save_state: bool) -> pd.DataFrame:
    """"""
    assert isinstance(
        file, str
    ), "please pass the path to a pickled pd.DataFrame object"
    try:
        database = pd.read_pickle(file)
        chunked = Chunker(
            chunk_by="length", expected_threshold=100, min_tolerable_threshold=75
        ).get_chunks(database)
        database_chunked = database.join(chunked).drop(
            columns=["subtitles", "timestamps"]
        )
        database_chunked.dropna(inplace=True)
        if save_state:
            save_to_cache("database", database_chunked)
        return database_chunked
    except pickle.UnpicklingError:
        sys.exit("The passed file does not point to a pickled pd.DataFrame object")


def render_recommendations_grid(
    recommendations: pd.DataFrame, mode: str, **grid_specs: int
):
    expander = st.beta_expander("Recommmendations", expanded=True)
    rows = min(
        int(len(recommendations) / grid_specs.get("rows", 3)), len(recommendations)
    )
    with expander:
        grid_pointer = 0
        for row in range(rows):
            columns = st.beta_columns(grid_specs.get("columns", 3))
            for column in columns:
                with column:
                    if mode == "search":
                        st.header(
                            f"{round(recommendations['cross-score'].iloc[grid_pointer] * 100, 2)}% :heart:"
                        )
                        st.video(
                            recommendations["video_link"].iloc[grid_pointer],
                            start_time=int(recommendations["start"].iloc[grid_pointer]),
                        )
                    else:
                        st.header(
                            f"{recommendations['video_title'].iloc[grid_pointer]}"
                        )
                        st.video(recommendations["video_link"].iloc[grid_pointer])
                grid_pointer += 1


def search_pipeline(recommender: Recommender, df: pd.DataFrame):
    st.header("Search")
    question = st.text_area(
        "Enter your question here", "How to make big decisions in life?"
    )
    if st.button("Search"):
        with st.spinner("Searching the database"):
            hits = recommender.search(question=question, corpus="blocks", top_k=200)
            recommendations = recommender.format_for_frontend(df, hits)
            render_recommendations_grid(
                recommendations, mode="search", columns=3, rows=3
            )
            st.dataframe(recommendations)
            st.dataframe(hits)


def explore_pipeline(recommender: Recommender):
    st.header("Explore")
    query = st.text_input("Search here", "love and relationships")
    if st.button("Explore"):
        with st.spinner("Searching the database"):
            hits, recommendations = recommender.explore(
                query=query, corpus=["video_title", "video_description"], top_k=10
            )
            # recommendations = recommender.format_for_frontend(df, hits)
            render_recommendations_grid(
                recommendations, mode="explore", columns=3, rows=3
            )
            st.dataframe(recommendations)
            st.dataframe(hits)

    raise NotImplementedError


# st.title("Ask Sadhguru")
# st.header("Search")
# question = st.text_area(
#     "Enter your question here", "How to make big decisions in life?"
# )
# search = st.beta_expander("Recommmendations", expanded=False)
# with search:
#     for i in range(1, 3):
#         col1, col2, col3 = st.beta_columns(3)
#         with col1:
#             st.header("Video 1")
#             st.video("https://www.youtube.com/watch?v=-2IcOOUqNgI", start_time=8)

#         with col2:
#             st.header("Video 2")
#             st.video("https://www.youtube.com/watch?v=-3rzessN6cI", start_time=6)

#         with col3:
#             st.header("Video 3")
#             st.video("https://www.youtube.com/watch?v=-46JXxFlXoA", start_time=92)

# st.header("Explore")
# question = st.text_input("Search here", "Sadhguru on Coronavirus pandemic")
# explore = st.beta_expander("Recommmendations", expanded=False)
# with explore:
#     for i in range(1, 3):
#         col1, col2, col3 = st.beta_columns(3)
#         with col1:
#             st.header("Video 1")
#             st.video("https://www.youtube.com/watch?v=-2IcOOUqNgI", start_time=8)

#         with col2:
#             st.header("Video 2")
#             st.video("https://www.youtube.com/watch?v=-3rzessN6cI", start_time=6)

#         with col3:
#             st.header("Video 3")
#             st.video("https://www.youtube.com/watch?v=-46JXxFlXoA", start_time=92)