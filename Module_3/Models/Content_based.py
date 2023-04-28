import pandas as pd
import numpy as np
import streamlit as st
from scipy.sparse import load_npz
from ast import literal_eval
import scipy
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_resource
def load_data_google(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)


interactions_df = load_data_google(st.secrets['interactions_url'])
books_selected = load_data_google(st.secrets['selected_books_url'])

books_selected['Genres'] = books_selected['Genres'].apply(lambda x: literal_eval(x) if "[" in x else x)
books_selected['Award'] = books_selected['Award'].apply(lambda x: literal_eval(x) if "[" in x else x)

# tfidf_matrix = np.load('https://drive.google.com/file/d/1FB7nf2GC2X5O7ZfDwjlXKuU4fmvoM_Ij/')
tfidf_matrix = load_npz("./pages/Datasets/tfidf_matrix.npz")
item_ids = books_selected['Uid'].tolist()


def get_item_profile(item_id):
    idx = item_ids.index(item_id)
    item_profile = tfidf_matrix[idx:idx + 1]
    return item_profile


def get_item_profiles(ids):
    item_profiles_list = [get_item_profile(x) for x in ids]
    item_profiles = scipy.sparse.vstack(item_profiles_list)
    return item_profiles


def build_users_profile(person_id, interactions_indexed_df):
    interactions_person_df = interactions_indexed_df.loc[person_id]

    if type(interactions_person_df['Uid']) == np.int64:
        ids = []
        ids.extend([interactions_person_df['Uid']])

    else:
        ids = interactions_person_df['Uid'].values


    user_item_profiles = get_item_profiles(ids)
    user_item_strengths = np.array(interactions_person_df['Review_Rating']).reshape(-1, 1)

    # Weighted average of item profiles by the interactions strength, and normalized
    user_item_strengths_weighted_avg = np.sum(user_item_profiles.multiply(user_item_strengths), axis=0) / np.sum(
        user_item_strengths)
    user_profile_norm = normalize(user_item_strengths_weighted_avg)

    return user_profile_norm


def build_users_profiles(new_user_df):
    interactions_indexed_df = new_user_df[new_user_df['Uid'].isin(books_selected['Uid'])].set_index('UserID')
    user_profiles = {}
    for person_id in interactions_indexed_df.index.unique():
        user_profiles[person_id] = build_users_profile(person_id, interactions_indexed_df)
    return user_profiles


class ContentBasedRecommender:
    MODEL_NAME = 'Content-Based'

    def __init__(self, items_df=None):
        self.item_ids = item_ids
        self.items_df = items_df

    def get_model_name(self):
        return self.MODEL_NAME

    def _get_similar_items_to_user_profile(self, person_id, new_user_profile, topn=1000):
        # Computes the cosine similarity between the user profile and all item profiles
        cosine_similarities = cosine_similarity(new_user_profile[person_id], tfidf_matrix)

        # Gets the top similar items & sort by similarity
        similar_indices = cosine_similarities.argsort().flatten()[-topn:]
        similar_items = sorted([(item_ids[i], cosine_similarities[0, i]) for i in similar_indices], key=lambda x: -x[1])

        return similar_items

    def recommend_items(self, user_id, user_profile, items_to_ignore=[], topn=10, verbose=False):
        similar_items = self._get_similar_items_to_user_profile(user_id, user_profile)
        # Ignores items the user has already interacted
        similar_items_filtered = list(filter(lambda x: x[0] not in items_to_ignore, similar_items))

        recommendations_df = pd.DataFrame(similar_items_filtered, columns=['Uid', 'Review_Rating']).head(topn)

        # If verbose is set to True, then the method returns a DataFrame that includes additional information
        # about the recommended items, such as their title, URL, and language.
        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(self.items_df, how='left',
                                                          left_on='Uid',
                                                          right_on='Uid')[['Review_Rating', 'Uid', 'Title']]

        return recommendations_df
