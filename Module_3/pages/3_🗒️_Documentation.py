import streamlit as st

st.set_page_config(
    page_title="Documentation",
    page_icon="🗒️",
    layout='wide'
)

st.title('🗒️ Documentation')

st.markdown(
    """
    In this page, we briefly mention several important components of our project for more smooth use of our systems.
    
    If you are interested in how to replicate our project, the main codes can be found 
    in our GitHub repository [GoodReads-Recommendation-System](https://github.com/YanboWang0204/GoodReads-Recommendation-System)
    
    ---
    """
)


st.subheader("Data Source")

st.markdown(
    """
    Our data is crawled from [GoodReads.com](https://www.goodreads.com/) Launched in 2007, which is now the world’s largest site 
    for readers and book recommendations. We collected **7776 books** from over 40 different genres and corresponding **114,063 reader reviews**.
    (*Data was collected until March, 2023*)
    
    The web crawler codes are also uploaded in GitHub, please see [GoodReads_web_crawler.py](https://github.com/YanboWang0204/GoodReads-Recommendation-System/blob/main/Module_1/GoodReads_web_crawler.py)
    and README.md for your references.
    
    Some information are only available for logged-in users, so please register an account on the website beforehand. 
    We manually code some prompts in the file to help you go through the complete process, please follow the prompt 
    instructions when running .py file. The main input users need to provide is about your web browswer `User-Agent` and 
    GoodReads website `Cookie`. The .py file will guide you to obtain these information. 
    If you have any difficulty in this process, you can contact @Yanbo by email.

    If everything goes well, you can obtain 3 datasets: `Book information`, `Book reviews`, and `Book statistics`.
    We also provide some Jupyter notebooks to guide you some tricky data cleansing procedures to replicate our final datasets.
    
    ---
    """
)

st.subheader('Data Visualization & Exploratory Analysis')

st.markdown(
    """
    After you have achieved the datasets, you can follow our notebooks for data visualization and exploratory analysis
    ([Notebook link](https://github.com/YanboWang0204/GoodReads-Recommendation-System/blob/main/Module_1/Notebooks/INDENG243_Project.ipynb))
    The main plotting packages we use are `Ployly` and`MatPlotLib`, also with some scientific packages like 'Scipy' and `pandas`.
     
    If you do not have code environments set up, don't worry! Just play with our page `Visualization & Exploratory Analysis`
    on left-hand sidebar where we provide some interactive tools for non-technical users. 
    You just click on these interactive plots and give it a go without worries about any codes!
    
    ---
    """

)


st.subheader('Recommendation System')

st.markdown(
    """
    For the main recommendation engine in our system, we mainly employed the following models:
    - Recommendation models
        - Popularity model (Baseline)
        - Content-based filtering
        - Collaborative filtering
        - Ensemble model
        
    The detailed description of these models' principles and implementation of codes can be found
    in our GitHub [Module 2 Notebook](https://github.com/YanboWang0204/GoodReads-Recommendation-System/blob/main/Module_2/Notebooks/INDENG243_Project_Module2.ipynb)
    
    If you simply want to play with our recommendation system, just click on the page `Recommendation System` on the 
    left-hand sidebar, where we try to provide an interactive procedures for recommending books you might find interested in
    based on your past reading preferences. Please be assured your data privacy is our first priority and your records will not be 
    stored in any server after you close our system.
    
    If you are not willing to provide these information or you cannot find your books read before, please simply click
    on the buttion `No book I have read before`, then our models will recommend the most popular books in your selected 
    genres. These results are based on open ratings from worldwide readers on `GoodReads.com`, partially representing
    some ideas from book lovers. Hope these functions can provide with you a pleasant experience when playing with our system.
    
    *P.S. If you use the system on your local host for the first time, please be patient to allow the system to 
    retrieve data from our cloud, which might take 2-5 minutes depending on your computer specs.*
    
    --- 
    """
)


st.subheader("Interaction tool vis Streamlit")

st.markdown(
    """
    Thanks to [Streamlit](https://streamlit.io/), a fantastic python package that allow developers to code 
    webpages and deploy Apps without too much front-end knowledge and provide a fascinating interaction tool for users.
    
    The main interaction tool is what you have seen so far on this webpage or App, just follow our guidelines,
    play with our functions and enjoy!
    
    If you have any problems, you can first refer to our project GitHub page or contact our main programmer @Yanbo
    for further assistance.
    
    ### 🎈 Hope you enjoy our system! 🎈
    """
)