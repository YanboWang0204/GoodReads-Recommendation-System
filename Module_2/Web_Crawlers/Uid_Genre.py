import requests
import os
from lxml import etree
import pandas as pd
import numpy as np
import time
import re


def uid_genre(session, headers, uid):
    format_url = 'https://www.goodreads.com/book/show/%s'
    page_stats = session.get(url=format(format_url % str(uid)), headers=headers).text
    tree = etree.HTML(page_stats)

    genres = []
    span_list = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[5]/ul/span[1]/span')
    for span in span_list[1:]:
        genres.extend(span.xpath('./a/span/text()'))

    if not genres:
        genres = ['N/A']

    uid_genre_df = pd.DataFrame({'Uid': [uid],
                                 'Genres': [genres]})
    uid_genre_df.to_csv('./uid_genre.csv', mode='a', index=False, header=False)

    pass


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cookie': 'ccsid=159-7930093-9537415; __qca=P0-1361510703-1675140696151; __gads=ID=8bdee2b028f48ea8:T=1675140697:S=ALNI_Mb3T4yBV0keqM4ZYY1skkrpV5LzqQ; csm-sid=401-6433125-3410995; srb_8=0_ar; lc-main=en_US; ubid-main=135-5942988-0104347; allow_behavioral_targeting=true; likely_has_account=true; session-id=135-3887267-7214224; csm-hit=tb:J6642CY04B39AYBVQAZJ+s-J6642CY04B39AYBVQAZJ|1675150266411&t:1675150266411&adb:adblk_no; session-id-time=2305870289l; session-token=qvyFSX8xzfwdWlT60v9Djx5MAEJQ8VEJJaYKDGsCGZEyr45nQQTwnWvViAAZVA9JQJj3tDG7XqmQg7UKsm59Tuj7Ne7NkvvrMFtdLK3SszdZUbX2zCylk/vYVHBKrHoFS7fer0BaB8CHRlk7ldJ++Rh556CL1MvNNOexPQ6ewFIfvwM0zOlP0IPDN+XGBRk7ZauP3/4aMBUAiSAJAcJyTu2uhWcznuHOOP2UQtg7FO4AoEDvWRC2lEOSGJm5i/iv; x-main="aw?A0ryleOVNJR@Vp6S92fIrEyMqZm0dDvoPZ7jhDpu1TVA?Vx?HzTJQeZyi1Qvv"; at-main=Atza|IwEBIBxIPJLtzTaZW38PFjTVzr3ttEHVuPwy6-K--zUMmt5zAtLr5WYPu44qfkTXB1Huonli4DhJZw0K9JlBWvHfK3vIoLQ0DSPF3Scideb3INBS6U5lGt0QASZMNfrd_WlBZzHUslCxTca6x7fgn3Q6A95Kvyj61VUpKSiVUajjsyMaQ9fu8X4ZInenOQtMBavNG-OVx1_GJSHLbiFGRErqhuzg6v_nZMvi44W_nHnkWrJlN6ApCgqssTxwIi8MOFczHQY; sess-at-main="TS3W6kQt7Yo4f2bvbNpFbvKnCaY7w93Zjg1hpdnHkC0="; __gpi=UID=000009389ed92c0e:T=1675140697:RT=1677189667:S=ALNI_MZL02vjB6yrUntv62VbaO-O6V11Pg; locale=en; _session_id2=ba58f27253fd7a90ad6f7878be640124'
    }

    # start a request session
    session = requests.Session()

    df_info = pd.read_csv('Book_info.csv')
    uid_df = df_info['Uid'].drop_duplicates().reset_index(drop=True)

    uid_get = pd.read_csv('./uid_genre.csv')['Uid'].values
    uid_miss = uid_df[~uid_df.isin(uid_get)]
    print(len(uid_miss))

    for index, uid in uid_miss.iteritems():
        print("Currently crawling %d book, uid is %d" % (index, uid))

        uid_genre(session=session, headers=headers, uid=uid)


