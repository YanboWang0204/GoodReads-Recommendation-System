import streamlit as st

st.set_page_config(
    page_title="Recommendation System",
    page_icon=":orange_book:",
    layout='wide'
)


import pandas as pd
import numpy as np
from ast import literal_eval
import time
import sys
sys.path.append("./Models")

# import models classes
from Popularity import PopularityRecommender
from Content_based import ContentBasedRecommender, build_users_profiles
from Collaborative_Filtering import CFRecommender
from Hybrid import HybridRecommender

from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import plotly.express as px
import plotly.graph_objects as go

st.title('📜 Recommendation System')
st.markdown(
    """
    ### 🎈 Welcome to our recommendation engines!
    
    With our recommendation system, we will first request you to choose some book genres you are curious about. 
    Our system will then provide a list of books of those genres from our database and ask you to give ratings on 
    books you might have read before.
    
    Then our fine-tuned models will recommend books you might be interested in and provide you with 
    some snapshots of their detailed information. 
    
    ##### 🤔 What if you have not read any books in the list but still want recommendations? 
    Don’t worry! In that case, we will recommend the highest rated books in your selected genres
    based on reader reviews from *GoodReads.com*.
    
    ---
    """
)


@st.cache_resource
def load_data_google(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)


@st.cache_data
def list_transform(df):
    df['Full_Genres'] = df['Full_Genres'].apply(lambda x: literal_eval(x) if "[" in x else x)
    df['Award'] = df['Award'].apply(lambda x: literal_eval(x) if "[" in x else x)
    return df


@st.cache_data
def list_transform_book(df):
    df['Genres'] = df['Genres'].apply(lambda x: literal_eval(x) if "[" in x else x)
    df['Award'] = df['Award'].apply(lambda x: literal_eval(x) if "[" in x else x)
    return df


@st.cache_data
def svd_pred(user_interactions_df):
    users_items_pivot_matrix_df = user_interactions_df.pivot(index='UserID',
                                                             columns='Uid',
                                                             values='Review_Rating').fillna(0)

    users_items_pivot_matrix = users_items_pivot_matrix_df.to_numpy()
    users_ids = list(users_items_pivot_matrix_df.index)

    users_items_pivot_sparse_matrix = csr_matrix(users_items_pivot_matrix)

    U, sigma, Vt = svds(users_items_pivot_sparse_matrix, k=23)
    sigma = np.diag(sigma)

    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
    all_user_predicted_ratings_norm = (all_user_predicted_ratings - all_user_predicted_ratings.min()) / \
                                      (all_user_predicted_ratings.max() - all_user_predicted_ratings.min())

    cf_preds_df = pd.DataFrame(all_user_predicted_ratings_norm, columns=users_items_pivot_matrix_df.columns,
                               index=users_ids).transpose()

    return cf_preds_df


def progress_bar():
    progress_text = "Your reading list recommendation is on the way!"
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(6):
        time.sleep(0.1)
        my_bar.progress(percent_complete * 20, text=progress_text)

    pass


# def button_callback():
#     if button_no_book not in st.session_state:
#         st.session_state.button_no_book = False
#         st.session_state.button_select = True

def text_percent(df):
    five_p = str(round(df['Five_star_percent'] * 100, 2)) + '%'
    four_p = str(round(df['Five_star_percent'] * 100, 2)) + '%'
    three_p = str(round(df['Five_star_percent'] * 100, 2)) + '%'
    two_p = str(round(df['Five_star_percent'] * 100, 2)) + '%'
    one_p = str(round(df['Five_star_percent'] * 100, 2)) + '%'

    # df['Percent_text'] = [five_p, four_p, three_p, two_p, one_p]

    pass


def display_bar():

    with st.container():
        book_interest = st.multiselect(
            "Are there any books in the above list that sparks your interest? Select them for more information!",
            book_rec_df['Title']
        )

        for book in book_interest:
            with st.expander(book):
                book_interest_df = books_df[books_df['Title'] == book]
                uid = book_interest_df['Uid'].values[0]

                c_img, c_info = st.columns(2)
                with c_img:
                    pic_url = book_pic_url[book_pic_url['Uid'] == uid]['URL'].values[0]
                    st.image(pic_url, width=300)

                with c_info:
                    st.metric(label='Book name', value=book)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label='Author', value=book_interest_df['Author'].values[0])

                    c2, c3, c4 = st.columns(3)
                    with c2:
                        st.metric(label='Average Rating', value=book_interest_df['Rating'].values[0])
                    with c3:
                        st.metric(label='Rating Number', value=book_interest_df['Rating_Num'].values[0])
                    with c4:
                        st.metric(label='Review Number', value=book_interest_df['Review_Num'].values[0])


                    fig_RatingDist = px.bar(book_interest_df,
                                            x=["Five_star_percent", "Four_star_percent",
                                               "Three_star_percent", "Two_star_percent", "One_star_percent"],
                                            text_auto=True,
                                            width=550, height=200)

                    fig_RatingDist.update_layout(yaxis={'visible': False, 'showticklabels': False},
                                                 xaxis={'visible': False},
                                                 title_text="Rating Distribution",
                                                 # xaxis_title='Percentage',
                                                 title_x=0,
                                                 # showlegend=False,
                                                 # legend=dict(
                                                 #     orientation="h",
                                                 #     yanchor="top",
                                                 #     xanchor="left",
                                                 #     font=dict(size=15)),
                                                 font=dict(size=18),
                                                 uniformtext_minsize=8, uniformtext_mode='hide')

                    st.plotly_chart(fig_RatingDist)
                # plot book stats
                stats_plot(book_interest_df)

                tag_list = book_tags[book_tags['Uid'] == uid]['Tags']
                book_sum = book_summary[book_summary['Uid'] == uid]

                st.markdown(
                    """
                    #### Book tags
                    """
                )
                # tag_str = ' '.join(tag_list)
                st.dataframe(tag_list)
                # st.write(tag_str)

                st.markdown(
                    """
                    #### Selected Book Reviews
                    """
                )
                book_sum_df = book_summary_process(book_sum)
                st.dataframe(book_sum_df, width=1200)

                url = 'https://www.goodreads.com/book/show/' + str(book_interest_df['Uid'].values[0])
                st.write("Book URL for more information: " + url)

    pass


@st.cache_data
def stats_plot(book_df):
    uid = book_df['Uid'].values[0]
    df_stats = book_stats[book_stats['Uid'] == uid]

    st.markdown(
        """
        #### Book statistics
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Times Added to Shelves", value=df_stats.iloc[0, 1])

    with c2:
        st.metric(label="Number of Ratings", value=df_stats.iloc[0, 2])

    with c3:
        st.metric(label="Number of Reviews", value=df_stats.iloc[0, 3])

    with c4:
        st.metric(label="Times marked as To-read", value=df_stats.iloc[0, 4])

    df_stats_day = df_stats.iloc[1:, :]

    c1, c2 = st.columns(2)
    with c1:
        p1 = go.Figure()
        p1.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['added'].values,
                                mode='lines+markers',
                                name='Added to shelves',
                                line=dict(color='firebrick', width=2)))
        p1.update_layout(width=500, height=300,
                         title_text='Added to shelves', title_x=0)
        st.plotly_chart(p1)

    with c2:
        p2 = go.Figure()
        p2.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['ratings'].values,
                                mode='lines+markers',
                                name='Ratings',
                                line=dict(color='orange', width=2)))
        p2.update_layout(width=500, height=300,
                         title_text='Ratings', title_x=0)
        st.plotly_chart(p2)

    c3, c4 = st.columns(2)
    with c3:
        p3 = go.Figure()
        p3.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['reviews'].values,
                                mode='markers',
                                name='Reviews',
                                line=dict(color='royalblue', width=2, dash='dot')))
        p3.update_layout(width=500, height=300,
                         title_text='Reviews', title_x=0)
        st.plotly_chart(p3)

    with c4:
        p4 = go.Figure()
        p4.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['to-read'].values,
                                mode='lines+markers',
                                name='to-read',
                                line=dict(color='green', width=2)))
        p4.update_layout(width=500, height=300,
                         title_text='To-read', title_x=0)
        st.plotly_chart(p4)

    pass


def book_summary_process(book_sum):
    summary = book_sum['Summary'].values[0]
    sum_split = summary.split('[SEP]')[:-2]
    return pd.DataFrame(sum_split, columns=['Summary'])


# load data

df_info = load_data_google(st.secrets['info_url'])
df_info = list_transform(df_info)

books_df = load_data_google(st.secrets['selected_books_url'])
books_df = list_transform_book(books_df)

interactions_df = load_data_google(st.secrets['interactions_url'])

# book tags & review summary
book_tags = load_data_google(st.secrets['book_tags_url'])
book_summary = load_data_google(st.secrets['book_summary_url'])[['Uid', 'Summary']]

# book picture URLs
book_pic_url = load_data_google(st.secrets['book_pic_url'])

# book stats
book_stats = load_data_google(st.secrets['stats_url'])


genre_selected = st.multiselect(
                        "Hi, please choose the book genres that you are curious for reading: ",
                        set(df_info['Genre']),
                        ['fiction', 'art']
)

df_select = df_info[df_info['Genre'].isin(genre_selected)]

book_selected = st.multiselect(
        "Please select the books that you have read and provide a rating for each book on a scale of 1 (worst) to 5 (best) to indicate your satisfaction level",
        df_select['Title'].unique()
)

if not book_selected:

    button_no_book = st.button("I have read none of these books")
    if 'button_no_book' not in st.session_state:
        st.session_state.button_no_book = False

    # if button_no_book:
    #     st.session_state.button_no_book = True
    #
    # if st.session_state.button_no_book:
    #     st.write("If no books you have read before, please take a look at the top-rating books in your curious genres:")
    #
    #     item_popularity_df = interactions_df.groupby('Uid')['Review_Rating'].sum().sort_values(
    #         ascending=False).reset_index()
    #
    #     popularity_model = PopularityRecommender(item_popularity_df, df_select)
    #     recommend_df = popularity_model.recommend_items()
    #
    #     book_rec_uid = recommend_df['Uid'].values
    #     book_rec_df = books_df[books_df['Uid'].isin(book_rec_uid)]
    #     st.dataframe(book_rec_df[['Title', 'Rating']])
    #
    #     with st.form("No book"):
    #         display_bar()
    #         st.form_submit_button("Submit Form")
    # if button_no_book:
    #     try:
    #         st.session_state.button_no_book = False
    #     except AttributeError:
    #         if 'button_no_book' not in st.session_state:
    #             st.session_state.button_no_book = True
    #     else:
    #         st.session_state.button_no_book = True

    if button_no_book:
        st.session_state.button_no_book = True

    if st.session_state.button_no_book:
        st.write("If have read none of the books listed, please take a look at the top-rating books in your curious genres:")

        uid_select = df_select['Uid'].unique()
        interactions_df_selected = interactions_df[interactions_df['Uid'].isin(uid_select)]
        item_popularity_df = interactions_df_selected.groupby('Uid')['Review_Rating'].sum().sort_values(
            ascending=False).reset_index()

        popularity_model = PopularityRecommender(item_popularity_df, df_select)
        recommend_df = popularity_model.recommend_items()

        book_rec_uid = recommend_df['Uid'].values
        book_rec_df = books_df[books_df['Uid'].isin(book_rec_uid)]
        st.dataframe(book_rec_df[['Title', 'Rating']].sort_values(by=['Rating'], ascending=False))

        # st.session_state.button_no_book = True
        display_bar()


else:
    # add new user info
    uid = df_select[df_select['Title'].isin(book_selected)]['Uid'].values
    n = len(book_selected)
    new_user_rating = []
    user_ID = [uid for uid in [13223456] for i in range(n)]

    for name in book_selected:
        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="Book name", value=name)

        with c2:
            rating = st.select_slider(
                "What's your rating for this book?",
                options=[1, 2, 3, 4, 5],
                key=name
            )
            new_user_rating.append(rating)

    # Content-based
    new_user_df = pd.DataFrame({"Uid": uid,
                                "UserID": user_ID,
                                "Review_Rating": new_user_rating})

    model = st.radio(
        "Please select a recommendation approach for you:",
        ('Based on your previous reading list and ratings', 'Based on readers with similar reading tastes', 'Based on the above two perspectives')
    )

    button = st.button("Run")
    if 'button' not in st.session_state:
        st.session_state.button = False

    if model == 'Based on your previous reading list and ratings':
        new_user_profile = build_users_profiles(new_user_df)

        content_based_recommender_model = ContentBasedRecommender(books_df)
        recommend_df = content_based_recommender_model.recommend_items(user_id=13223456, user_profile=new_user_profile,
                                                                       items_to_ignore=uid)
        book_rec_uid = recommend_df['Uid'].values
        book_rec_df = books_df[books_df['Uid'].isin(book_rec_uid)]

        if button:
            st.session_state.button = True

        if st.session_state.button:
            progress_bar()
            st.write("Based on your ratings, we guess the following books might be your favourites!")
            st.dataframe(book_rec_df[['Title', 'Rating']].sort_values(by=['Rating']))
            st.balloons()

            # st.session_state.button = True
            display_bar()

    if model == 'Based on readers with similar reading tastes':
        # Collaborative filtering

        total_interactions_df = pd.concat([interactions_df[['Uid', 'UserID', 'Review_Rating']], new_user_df], axis=0)

        cf_preds_df = svd_pred(total_interactions_df)

        cf_recommender_model = CFRecommender(cf_preds_df, books_df)
        book_rec_cf = cf_recommender_model.recommend_items(user_id=13223456, items_to_ignore=uid)

        book_cf_uid = book_rec_cf['Uid'].values
        book_rec_df = books_df[books_df['Uid'].isin(book_cf_uid)]

        if button:
            st.session_state.button = True

        if st.session_state.button:
            progress_bar()
            st.write("Based on users who have similar tastes as you,  we guess the following books might be your favourites!")
            st.dataframe(book_rec_df[['Title', 'Rating']].sort_values(by=['Rating']))
            st.balloons()

            # st.session_state.button = True
            display_bar()

    if model == 'Based on the above two perspectives':
        # Hybrid models
        new_user_profile = build_users_profiles(new_user_df)
        content_based_recommender_model = ContentBasedRecommender(books_df)

        total_interactions_df = pd.concat([interactions_df[['Uid', 'UserID', 'Review_Rating']], new_user_df], axis=0)
        cf_preds_df = svd_pred(total_interactions_df)
        cf_recommender_model = CFRecommender(cf_preds_df, books_df)

        hybrid_recommender_model = HybridRecommender(content_based_recommender_model, cf_recommender_model, books_df,
                                                     cb_ensemble_weight=1.0, cf_ensemble_weight=1.0)

        book_rec_hybrid = hybrid_recommender_model.recommend_items(user_id=13223456, user_profile=new_user_profile,
                                                                   items_to_ignore=uid)

        book_hybrid_uid = book_rec_hybrid['Uid'].values
        book_rec_df = books_df[books_df['Uid'].isin(book_hybrid_uid)]

        if button:
            st.session_state.button = True

        if st.session_state.button:
            progress_bar()
            st.write("Based on your ratings & other similar users' tastes, we guess the following books might be your favourites!")
            st.dataframe(book_rec_df[['Title', 'Rating']].sort_values(by=['Rating']))
            st.balloons()

            # st.session_state.button = True
            display_bar()

        # if button or st.session_state.button:
        #     progress_bar()
        #     st.write("Based on your ratings & other similar users' tastes, we guess the following books might be your favourites!")
        #     st.dataframe(book_rec_df[['Title', 'Rating']])
        #     st.balloons()
        #
        #     st.session_state.button = True
        #     display_bar()


