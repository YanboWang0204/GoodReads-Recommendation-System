import streamlit as st
import pandas as pd
import numpy as np
from ast import literal_eval

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(
    page_title="Visualization & EDA",
    page_icon=":bar_chart:",
    layout='wide'
)

st.title('📊 Visualization & Exploratory Analysis')


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
def award_encode(df):
    df = df.reset_index(drop=True)
    award_set = set([])
    for index, award_list in df['Award'].items():
        award_set.update(award_list)

    award_df = pd.DataFrame(columns=award_set)
    award_df = award_df.sort_index(axis=1)

    award_data = np.zeros((len(df['Award']), len(award_set)))

    for index, award_list in df['Award'].items():
        for award in award_list:
            # if award exists in this book's award entry, we retrieve its index and put '1' to encode
            if award in list(award_df.columns):
                col_index = list(award_df.columns).index(award)
                award_data[index, col_index] = 1

    award_count = pd.DataFrame(award_data, columns=award_df.columns, dtype='int64')
    return award_count


@st.cache_data
def percentage_process(df):
    df['Five_star_percent'] = df['Five_Star'] / df['Rating_Num']
    df['Four_star_percent'] = df['Four_Star'] / df['Rating_Num']
    df['Three_star_percent'] = df['Three_Star'] / df['Rating_Num']
    df['Two_star_percent'] = df['Two_Star'] / df['Rating_Num']
    df['One_star_percent'] = df['One_Star'] / df['Rating_Num']
    return df_info


@st.cache_data
def percentage_df(df):
    p_df = pd.DataFrame()
    p_df['Genre'] = df['Genre'].unique()
    p_df['Five_Star_Percentage'] = df['Five_Star'].sum() / df['Rating_Num'].sum() * 100
    p_df['Four_Star_Percentage'] = df['Four_Star'].sum() / df['Rating_Num'].sum() * 100
    p_df['Three_Star_Percentage'] = df['Three_Star'].sum() / df['Rating_Num'].sum() * 100
    p_df['Two_Star_Percentage'] = df['Two_Star'].sum() / df['Rating_Num'].sum() * 100
    p_df['One_Star_Percentage'] = df['One_Star'].sum() / df['Rating_Num'].sum() * 100
    return p_df


def col_num(x):
    if x % 4 == 0:
        return 4
    else:
        return x % 4


def row_num(x):
    if x % 4 == 0:
        return x // 4
    else:
        return x // 4 + 1


def best_row_col_num(n):
    row = 1
    col = 1
    if n <= 4:
        row = 1
        col = n
    if n > 4:
        col = 4
        row = row_num(n)
    return row, col


st.subheader('Book information Datasets')
st.markdown(
    """
    The following is a snapshot of book information dataset, which contains the following attributes:
    """
)

# df_info = load_data_google('https://docs.google.com/spreadsheets/d/1pKiV2vD3ZTvjqg0EYyYa9-3whnVaFhGQoYQCHlk7GRE/edit#gid=1668223231')
df_info = load_data_google(st.secrets['info_url'])
df_info = list_transform(df_info)

st.dataframe(df_info.head(10))

# book_stats = load_data_google('https://docs.google.com/spreadsheets/d/1Oxbmc_OP3GTwPiXhYyoXUVK-pEgancDejCpBFHlF6bc/edit#gid=726264491')
book_stats = load_data_google(st.secrets['stats_url'])

subtab_overview, subtab_genre = st.tabs(['**Overview**', '**Genre**'])

df_info_category_extract = df_info[['Genre','Rating','Review_Num','Rating_Num','Five_Star','Four_Star','Three_Star','Two_Star','One_Star']]

# Compute the average statistics for each genre
df_info_category = df_info_category_extract.groupby(['Genre'], as_index=False).mean()


df_info_category['Five_Star_Percentage'] = df_info_category['Five_Star']/ df_info_category['Rating_Num'] * 100
df_info_category['Four_Star_Percentage'] = df_info_category['Four_Star']/ df_info_category['Rating_Num'] * 100
df_info_category['Three_Star_Percentage'] = df_info_category['Three_Star']/ df_info_category['Rating_Num'] * 100
df_info_category['Two_Star_Percentage'] = df_info_category['Two_Star']/ df_info_category['Rating_Num'] * 100
df_info_category['One_Star_Percentage'] = df_info_category['One_Star']/ df_info_category['Rating_Num'] * 100

with subtab_overview:
    st.subheader('Overview')
    st.markdown(
        """
        #### Average Rating v.s. Genre
        - To gain a broad understanding of book ratings, we analyzed the average ratings across different genres.
        """
    )
    fig = px.scatter(df_info_category, y="Rating", x="Genre", color='Genre', width=1000, height=500)
    fig.update_layout(title='Average Rating v.s. Genre', title_x=0.35)
    fig.update_traces(marker_size=10)

    st.plotly_chart(fig)

    st.markdown(
        """
        #### Rating Distribution v.s. Genre
        For *Ratings*, we would like to take a deeper look at its inner distributions across genres. 
        - We visualized the rating distributions across genres. It shows the percentage of different scores for each genre.
        """
    )
    fig_Rating_Breakdown = px.bar(df_info_category, y="Genre",
                                  x=["Five_Star_Percentage", "Four_Star_Percentage",
                                     "Three_Star_Percentage", "Two_Star_Percentage", "One_Star_Percentage"],
                                  width=900, height=700)
    fig_Rating_Breakdown.update_layout(title_text='Rating Distributions across Genres', xaxis_title='Percentage',
                                       title_x=0.4)
    st.plotly_chart(fig_Rating_Breakdown)

    st.markdown(
        """
        #### Rating/Review Number v.s. Genre
        In addition to ratings, another important numerical features in our dataset are the ***Rating numbers*** and ***Review numbers*** (i.e. how many users write a reivew/rate this book). These two features can indicate the **popularity** (or trend) of the book among readers, thus very important for book recommendations.

        *(Their difference is that for a review, users need to have textual comments, but rating only requires users to rate books in stars.)*

        So we will take a look at the plots of the average rating numbers and review numbers across genres.
        """
    )

    fig_Rating_Num = px.scatter(df_info_category, x="Genre", y="Rating_Num", color='Genre', width=1000, height=500)
    fig_Rating_Num.update_layout(title_text='Average Rating Numbers v.s. Genre', title_x=0.35)
    fig_Rating_Num.update_traces(marker_size=10)
    st.plotly_chart(fig_Rating_Num)

    fig_Review_Num = px.scatter(df_info_category, x="Genre", y="Review_Num", color='Genre', width=1000, height=500)
    fig_Review_Num.update_layout(title_text='Average Review Numbers v.s Genre', title_x=0.35)
    fig_Review_Num.update_traces(marker_size=10)
    st.plotly_chart(fig_Review_Num)

    st.markdown(
        """
        #### Rating v.s. Review/Rating Number across genres
        - We first visualized the ***review number*** vs ***rating*** in a bubble chart. The size of each bubble is the review number.
        """
    )

    fig_Review_Num_Rate = px.scatter(df_info_category, x="Rating", y="Review_Num", size="Review_Num",
                                     color="Genre", hover_name="Genre", size_max=60, width=900, height=500)
    fig_Review_Num_Rate.update_layout(title_text='Review Number v.s. Rating across Genres', title_x=0.4)
    st.plotly_chart(fig_Review_Num_Rate)

    st.markdown(
        """
        - Then we visualized ***rating numbers*** vs ***ratings*** in histograms. 
        These graphs illusrated the distribution of ratings versus number of ratings it received for each genre as well as 
        the distribution of different genres given a specific rating.
        
        """
    )

    fig_Rating_RateNum = px.histogram(df_info, x="Rating", y="Rating_Num", color="Genre", marginal="violin",
                       hover_data=["Genre", "Rating"], nbins=80, width=900, height=900)
    fig_Rating_RateNum.update_layout(margin=dict(l=20, r=20, t=25, b=20), title_text='Rating Num v.s. Rating across Genres',
                      title_x=0.4)
    st.plotly_chart(fig_Rating_RateNum)

    st.markdown(
        """
        #### Award across genres visualization

        There are many literary awards, which help readers to select high-quality books. 
        In this section, we study the genre distribution of award-winning books to understand the general trend 
        and potential preference for different awards.
        
        In order to provide a more representative result, we focus on the Top 20 prestigious awards based on the record numbers of awards. 
        """
    )

    award_count = award_encode(df_info)
    award_series = award_count.sum().sort_values(ascending=False)[1:21]

    st.markdown(
        """
        #### Genre Distribution in Awards
        - Among the selected Top 20 awards, we first summarized the genres of the award-winning books to examine award preference in general.
        - Also we calculated the total number of awards each genre wins
        """
    )

    df_award = pd.concat([df_info[['Genre']], award_count[award_series.index.values]], axis=1)
    award_genre = df_award.groupby('Genre').sum().reset_index()
    award_genre.head()

    total_awards = pd.DataFrame({'Genre': award_genre['Genre'],
                                 'Total_Awards': award_genre.iloc[:, 1:].sum(axis=1)})

    c1, c2 = st.columns(2)

    with c1:
        fig_df = go.Figure(data=[go.Table(
                    header=dict(values=list(total_awards.columns),
                                line_color='darkslategray',
                                fill_color='grey',
                                font=dict(color='white', size=12)
                                ),
                    cells=dict(values=[total_awards.Genre, total_awards.Total_Awards],
                               line_color='darkslategray',
                               fill_color=[['white', 'lightgrey'] * 10 * 2]))])
        fig_df.update_layout(height=600, width=500)
        st.plotly_chart(fig_df)

    with c2:
        fig_totalAward = px.pie(total_awards, values='Total_Awards', names='Genre',
                                title='Awards Distribution across Genres in Top 20 Awards')

        fig_totalAward.update_traces(textposition='inside', hole=0.3)

        fig_totalAward.update_layout(margin=dict(l=0, r=0, t=25, b=15),
                                    uniformtext_minsize=20,
                                    uniformtext_mode='hide',
                                    height=500, width=600,
                                    title_x=0.2)
        st.plotly_chart(fig_totalAward)

    st.markdown(
        """
        #### Genre Distributions in *Individual* Award

        - In addition to an overview of the award winning frequencies across genres, we also examine the distribution of genres 
        in ***individual*** award seperately, taking into account the different criteria and preferences that may cause different effects.
        - This is to examine the ***Simpon's paradox***, which concerns about the overall trend will be overturned when dividing into sub-populations
        """
    )

    award_names = list(award_genre.columns.values[1:])
    award_selected = st.multiselect(
                        "Please choose the award you are curious about: ",
                        award_names,
                        ['hugo_award', 'locus_award', 'nebula_award'])
    if not award_selected:
        st.error("Please select at least one award!")

    else:
        n = len(award_selected)
        row, col = best_row_col_num(n)

        specs = [[{'type': 'domain'}] * col] * row
        fig_AwardSelect = make_subplots(rows=row, cols=col, specs=specs, subplot_titles=award_selected)
        for i in award_selected:
            index = award_selected.index(i) + 1
            fig_AwardSelect.add_trace(go.Pie(labels=award_genre['Genre'], values=award_genre[i], name=i),
                                      row=row_num(index),
                                      col=col_num(index))
            fig_AwardSelect.update_traces(textposition='inside')
            fig_AwardSelect.update_layout(margin=dict(l=0, r=20, t=70, b=15),
                                          height=600, width=1000,
                                          uniformtext_minsize=10,
                                          uniformtext_mode='hide')
        st.plotly_chart(fig_AwardSelect)

    st.markdown(
        """
        #### Rating distribution
        - Box plot & violin plot
        """
    )

    fig_dist = go.Figure()

    fig_dist.add_trace(go.Box(
        y=df_info['Rating'],
        name="Boxplot",
        jitter=0.3,
        pointpos=-1.8,
        marker_color='rgb(7,40,89)',
        line_color='rgb(7,40,89)'
    ))

    fig_dist.add_trace(go.Violin(
        y=df_info['Rating'],
        name="Violin plot",
        marker_color='rgb(9,56,125)',
        line_color='rgb(9,56,125)'
    ))

    fig_dist.update_layout(title_text='Rating distribution',
                           title_x=0.4,
                           height=600,
                           width=1000)
    st.plotly_chart(fig_dist)


    st.markdown(
        """
        #### Correlation & Heatmap
        """
    )
    df_info = percentage_process(df_info)
    labels = ['Rating', 'Page_Num', 'Book_Authored', 'Review_Num', 'Rating_Num', 'Follower_Num',
              'Five_star_percent', 'Four_star_percent', 'Three_star_percent', 'Two_star_percent', 'One_star_percent']

    df_corr = df_info[labels].corr().values
    fig_heat = px.imshow(df_corr, x=labels, y=labels,
                         color_continuous_scale='Viridis',
                         aspect="auto")
    fig_heat.update_traces(text=np.around(df_corr, decimals=2), texttemplate="%{text}")
    fig.update_xaxes(side="bottom")
    fig_heat.update_layout(width=900, height=800)
    st.plotly_chart(fig_heat)


with subtab_genre:
    st.subheader('Genre')

    genre_selected = st.selectbox(
                        "Choose one genre from below",
                        set(df_info['Genre'].unique())
    )

    print(genre_selected)
    df_select = df_info[df_info['Genre'] == genre_selected]
    p_df = percentage_df(df_select)

    st.markdown(
        """
        Genre information board
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Genre name", value=genre_selected)

    with c2:
        st.metric(label="Average Rating", value=np.round(df_select['Rating'].mean(), 2))

    with c3:
        st.metric(label="Average Rating number", value=int(df_select['Rating_Num'].mean()))

    with c4:
        st.metric(label="Average Review number", value=int(df_select['Review_Num'].mean()))

    fig_RatingDist = px.bar(p_df, y='Genre',
                            x=["Five_Star_Percentage", "Four_Star_Percentage",
                               "Three_Star_Percentage", "Two_Star_Percentage", "One_Star_Percentage"],
                            text_auto=True,
                            width=1200, height=200)

    fig_RatingDist.update_layout(yaxis={'visible': False, 'showticklabels': False},
                                 title_text="Rating Distribution",
                                 xaxis_title='Percentage',
                                 title_x=0.4,
                                 uniformtext_minsize=8, uniformtext_mode='hide')

    st.plotly_chart(fig_RatingDist)

    st.markdown(
        """
        Award winning under this genre
        - Total number of awards won for books under this genre 
        """
    )
    award_genre = award_encode(df_select).sum().sort_values(ascending=False)
    award_genre_df = pd.DataFrame(data=award_genre, columns=['Num'])
    award_genre_df.reset_index(inplace=True)

    award_genre_df = award_genre_df.rename(columns={'index': 'Award_Name'}).iloc[1:, :]

    fig_table = go.Figure(data=[go.Table(
                            header=dict(values=list(award_genre_df.columns),
                                        line_color='darkslategray',
                                        fill_color='grey',
                                        font=dict(color='white', size=16)
                                        ),
                            cells=dict(values=[award_genre_df.Award_Name, award_genre_df.Num],
                                       line_color='darkslategray',
                                       fill_color=[['white', 'lightgrey'] * len(award_genre_df) * 2],
                                       font=dict(color='black', size=14),
                                       height=30))]
    )
    fig_table.update_layout(height=600, width=800)
    st.plotly_chart(fig_table)

    # Book statistics dashboard
    book_selected = st.selectbox(
        "Choose a book under this genre you are interested in",
        df_select['Title'].unique()
    )

    uid = df_select[df_select['Title'] == book_selected]['Uid'].values[0]
    df_stats = book_stats[book_stats['Uid'] == uid]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Added", value=df_stats.iloc[0, 1])

    with c2:
        st.metric(label="Ratings", value=df_stats.iloc[0, 2])

    with c3:
        st.metric(label="Reviews", value=df_stats.iloc[0, 3])

    with c4:
        st.metric(label="To-read", value=df_stats.iloc[0, 4])

    df_stats_day = df_stats.iloc[1:, :]

    c1, c2 = st.columns(2)
    with c1:
        p1 = go.Figure()
        p1.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['added'].values,
                                mode='lines+markers',
                                name='Added',
                                line=dict(color='firebrick', width=2)))
        p1.update_layout(width=550, height=400,
                         title_text='Added', title_x=0.4)
        st.plotly_chart(p1)

    with c2:
        p2 = go.Figure()
        p2.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['ratings'].values,
                                mode='lines+markers',
                                name='Ratings',
                                line=dict(color='orange', width=2)))
        p2.update_layout(width=550, height=400,
                         title_text='Ratings', title_x=0.4)
        st.plotly_chart(p2)

    c3, c4 = st.columns(2)
    with c3:
        p3 = go.Figure()
        p3.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['reviews'].values,
                                mode='markers',
                                name='Reviews',
                                line=dict(color='royalblue', width=2, dash='dot')))
        p3.update_layout(width=550, height=400,
                         title_text='Reviews', title_x=0.4)
        st.plotly_chart(p3)

    with c4:
        p4 = go.Figure()
        p4.add_trace(go.Scatter(x=df_stats_day['date'].values,
                                y=df_stats_day['to-read'].values,
                                mode='lines+markers',
                                name='to-read',
                                line=dict(color='green', width=2)))
        p4.update_layout(width=550, height=400,
                         title_text='To-read', title_x=0.4)
        st.plotly_chart(p4)

