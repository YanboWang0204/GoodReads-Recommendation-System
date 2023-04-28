import streamlit as st

st.set_page_config(
    page_title="Hello Page",
    page_icon="📚",
    layout='wide'
)

st.title("📚 *GoodReads*: Book Analytics & Recommendation System")
st.markdown(
    """
    - @Group 18
    - @Member: Yanbo Wang, Yinuo Hu, Shichen Wu, Jiaming Xiong, Xinlin Huang, Wenxuan Yang
    - @GitHub: [GoodReads-Recommendation-System](https://github.com/YanboWang0204/GoodReads-Recommendation-System)
    ---
    
    This webpage app is built specifically for demonstrating our group project about
    building an intelligent book recommendation system based on data from *GoodReads.com*.
    
    👈 **You can switch different pages on left-hand sidebar to play with different functions**
    """
)

st.subheader('📊 Visualization & Exploratory Analysis')
st.markdown(
    """
    In this module, we conducted data visualization & exploratory data analysis on crawled data from *[GoodReads.com](https://www.goodreads.com/)*.
    
    Here we provide an overview of datasets and classify books by their genres where you can select the book genres you 
    are curious about in the multi-select boxes for more specific visualization.
    """
)

st.subheader('📜 Recommendation System')
st.markdown(
    """
    This is the main module for our recommendation system. You can try our system by following up 
    procedures described in pages. The main models used in our system are described as follows:
    - Recommendation models
        - Popularity model (Baseline)
        - Content-based filtering
        - Collaborative filtering
        - Ensemble model
    
    We also explored some NLP models to provide executive review of book content and reviews, 
    which can help users quickly grasp a screenshot of books recommended to them.
    
    - **Tag filtering system**: we want to extract tags for each book to enable users to filter books & comments by tags
        - Topic Modeling: LDA method
        - Keywords Extraction: TextRank
        - Keyphrases Extraction: Yake!, keyBERT, Rake, etc. 
    
    
    - **Extractive Summarization**: Extract top review sentences to serve as a summary of all reviews of each book
        - Baseline approach
        - Balanced summarization
    """
)

st.subheader('🗒️ Documentation')
st.markdown(
    """
    Explanation of several important components of project, including:
    - Data source
    - Data Visualization & Exploratory Analysis
    - Recommendation System
    - Interaction tool vis Streamlit
    """
)

st.subheader('📅 Future Plans')
st.markdown(
    """
    Based on our current work, we have deployed this app to help potential users to generate their unique
    to-read book lists. As a next step, we will broader our database and pursue a higher recommendation accuracy to 
    provide better experiences for our users.
    """
)

st.markdown(
    """
    ---
    Version 1.0, copyright by Yanbo Wang (IEOR, UC Berkeley)
    """
)

c1, c2, c3 = st.columns(3)

with c1:
    st.info('**GitHub: [@GoodReads-Recommendation-System](https://github.com/YanboWang0204/GoodReads-Recommendation-System)**', icon="💻")

with c2:
    st.info('**Contact: [@Yanbo Wang](yanbo.wang@berkeley.edu)**', icon="📩")

with c3:
    st.info('**References: [@INDENG 243: Analytics Lab](https://bcourses.berkeley.edu/courses/1522176)**', icon="🏫")
