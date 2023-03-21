# GoodReads-Recommendation-System
### @Group 18 <br>
### @Yanbo Wang, Yinuo Hu, Jiaming Xiong, Xinlin Huang, Shichen Wu, Wenxuan Yang
---

This is a repository for UC Berkeley INDENG 243: Analytics Lab Group Project

## Module 1 - Exploratory Analysis

Please download the folder `Module_1` for datasets, codes and notebooks. Below are some instructions for usage:

### Datasets

This time we directly scraped data from [GoodReads.com](https://www.goodreads.com/) website. For the detailed web crawler code, please see `GoodReads_web_crawler.py` for further information.

Some information are only available for logged-in users, so please register an account on the website beforehand. We manually code some prompts in the file to help you go through the complete process, please follow the prompt instructions when running .py file. The main input users need to provide is about your web browswer `User-Agent` and GoodReads website `Cookie`. The .py file will guide you to obtain these information. If you have any difficulty in this process, you can contact @Yanbo by email. <br>

If everything goes well, you can obtain 3 datasets: `Book information`, `Book reviews`, and `Book statistics`.

The original scraped datasets are enormous, so we only upload a sample data (10 books for each genre) for experimental use, please see `book_stats` folder for source files (first compress .zip file). To avoid the loss of all previous information when the web scraping is interrupted by unexpected error, we stored each book's information as a single CSV file. Then after scraping is done, we combine them together into two comprehensive CSVs (detailed codes of this process can be found in [Data_preprocessing.ipynb](./Module_1/Notebooks/Data_preprocessing.ipynb)):
- Book_info.csv
- Book_reviews.csv

(*Book statistics are hard to be combined in one CSV file, so we leave them as single files*)

Here due to the repository storage limit (<= 100MB), we compressed the `Book_reviews.csv` and `Book_reviews_cleaned.csv` (cleaned datasets CSV) into .zip file, please first decompress these two zip files for use.

### Jupyter notebooks usage

The main codes for Module 1 are stored in [INDENG243_Project.ipynb](./Module_1/Notebooks/INDENG243_Project.ipynb), you can simply follow the instructions in that notebook to run our codes sequentially by order.

Among them, the 2.1.1 `Data pre-processing` part and `Interactive plots` are stored as separate Jupyter notebooks to avoid some problems caused by incomplete datasets and display problem of interactive plots in HTML. 

If you are interested in the whole organization of codes, you can simply start from the fist line in notebook to get a big picture of our project. 

If you are only interested in data visualization codes, you can start from part 3  `Data visualization` and directly use the cleaned datasets:
- Book_info_cleaned.csv
- Book_reviews_cleaned.csv

The part 5 about `textual data exploration` might take a longer time for running, actually it runs about 1 hour on our laptop, so you might jump out this process or simply visualize the output results in our notebook.

### Report

The report for Module 1 is also uploaded in the folder `Module_1`, named as [INDENG243 Module 1 Report - Group 18](./Module_1/INDENG243_Module1_Report_Group18.pdf)

---

## Module 2 - Systems Analytics

Please download the folder `Module_2` for datasets, codes and notebooks. Below are some instructions for usage:

### Datasets

This time we conducted some modifications on original datasets, you can first download original datasets from [Module 1 Datasets](./Module_1/Datasets) to completely replicate our process of getting datasets for final use. If you simply want to use the updated ones, please see [Module 2 Datasets Basic_Datasets](./Module_2/Datasets/Basic_datasets) for all completed datasets. 

We added some additional data and the corresponding web scraping codes can be found in `Uid_genre.py` & `Genre_Book_Add.py`. The main jupyter notebook will discuss why we need these additional data.

Since this part involves many variations of datasets (corresponding to different operations we have done for model use), I created some sub-folders under [Datasets](./Module_2/Datasets) to help classify their uses and make files organized:
- **Partial_Datasets**: Some intermediate files before reaching our final ones, you can use them if you want to completely replicate the whole process (Part 1)
- **Basic_datasets**: The base datasets for book information & book reviews, the datasets used mainly in the part `Model data preparation` and NLP models (Part 1 & 3);
- **Rec_models_datasets**: The selected data for recommendation models' use (Part 2);

P.S. Remember to first decompress the .zip files before use and put them into your working directory to take care of path problems.

### Jupyter notebooks & NLP codes

The main part is included in notebook [INDENG243_Project_Module2.ipynb](./Module_2/Notebooks/INDENG243_Project_Module2.ipynb) and we put some repeated and lengthy data cleansing for new additional data into a separate notebook [Data_Revise_Cleansing.ipynb](./Module_2/Notebooks/Data_Revise_Cleansing.ipynb) if you like.

This time apart from the main recommendation models, we also explore some NLP models and their codes are generally hard to be run in jupyter notebooks, so we mainly run them in IDE and put some result screenshots and markdowns for explanations in notebook. Please see [NLP_Models](./Module_2/NLP_Models) if you are interested in the original codes.

Under `Notebook` folder, you can see `output` for NLP models and some `pictures` for results' screenshots and demonstration used in notebooks.

### Report

The report for Module 2 is also uploaded in the folder `Module_2`, named as [INDENG243 Module 2 Report - Group 18](./Module_2/INDENG243_Module2_Report_Group18.pdf)



