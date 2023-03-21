# GoodReads-Recommendation-System
### @Group 18 <br>
### @Yanbo Wang, Yinuo Hu, Jiaming Xiong, Xinlin Huang, Shichen Wu, Wenxuan Yang
---

This is a repository for UC Berkeley INDENG 243: Analytics Lab Group Project

## Module 2 - Systems Analytics

Please download the folder `Module_2` for datasets, codes and notebooks. Below are some instructions for usage:

### Datasets

This time we conducted some modifications on original datasets, you can first download original datasets from [Module 1 Datasets](./Module_1/Datasets) to completely replicate our process of getting datasets for final use. If you simply want to use the updated ones, please see [Module 2 Datasets Basic_Datasets](./Module_2/Datasets/Basic_Datasets) for all completed datasets. 

We added some additional data and the corresponding web scraping codes can be found in `Uid_genre.py` & `Genre_Book_Add.py`. The main jupyter notebook will discuss why we need these additional data.

Since this part involves many variations of datasets (corresponding to different operations we have done for model use), I created some sub-folders under [Datasets](./Module_2/Datasets) to help classify their uses and make files organized:
- **Partial_Datasets**: Some intermediate files before reaching our final ones, you can use them if you want to completely replicate the whole process (Part 1)
- **Basic_datasets**: The base datasets for book information & book reviews, the datasets used mainly in the part `Model data preparation` and NLP models (Part 1 & 3);
- **Rec_models_datasets**: The selected data for recommendation models' use (Part 2);

### Jupyter notebooks & NLP codes

The main part is included in notebook [INDENG243_Project_Module2.ipynb](./Module_2/Notebooks/INDENG243_Project_Module2.ipynb) and we put some repeated and lengthy data cleansing for new additional data into a separate notebook [Data_Revise_Cleansing.ipynb](./Module_2/Notebooks/Data_Revise_Cleansing.ipynb) if you like.

This time apart from the main recommendation models, we also explore some NLP models and their codes are generally hard to be run in jupyter notebooks, so we mainly run them in IDE and put some result screenshots and markdowns for explanations in notebook. Please see [NLP_Models](./Module_2/NLP_Models) if you are interested in the original codes.

Under `Notebook` folder, you can see `output` for NLP models and some `pictures` for results' screenshots and demonstration used in notebooks.

### Report

The report for Module 2 is also uploaded in the folder `Module_2`, named as [INDENG243 Module 2 Report - Group 18](./Module_2/INDENG243_Module2_Report_Group18.pdf)



