import requests
import os
from lxml import etree
import pandas as pd
import re
from langdetect import detect  # package for filtering non-English reviews
from string import punctuation


def genre_name_modify(text):
    """
    transform genre names into more elegant form, e.g. children\s -> children-s, remove empty space
    @param text:
    @return: formatted genre name
    """
    text = str.lower(text)
    text = text.replace(' ', '-')
    text = text.replace('\'', '-')
    return text


def book_stats(session, headers, uid):
    """
    retrieve current book's statistics data
    @param session: current request session
    @param headers: session headers
    @param url: current book's statistic url
    @param genre: current book's genre belonging to
    @param book_name: current book's name

    @return: store book stats as a csv file
    """
    stats_url = 'https://www.goodreads.com/book/stats/' + uid
    page_stats = session.get(url=stats_url, headers=headers).text
    tree = etree.HTML(page_stats)

    # overall statistics
    stats_box = tree.xpath('//div[@class="reviewStatsBox"]/div')

    rating = digit_process(stats_box[1].xpath('./div[2]/text()'))
    review = digit_process(stats_box[2].xpath('./div[2]/text()'))
    to_read = digit_process(stats_box[3].xpath('./div[2]/text()'))
    add_shelf = digit_process(stats_box[4].xpath('./div[2]/text()'))

    # daily data
    tr_list = tree.xpath('//table[@id="books_added_table"]/tr')

    stats_list = [['Overall', add_shelf, rating, review, to_read]]
    # data starting from the third tr tag
    for tr in tr_list[2:]:
        stats_list.append(tr.xpath('./td/text()'))

    stats_df = pd.DataFrame(data=stats_list, columns=['date', 'added', 'ratings', 'reviews', 'to-read'])
    stats_df.to_csv('./GoodReads_stats/book_stats/' + uid + '_stats.csv', index=False)

    pass


def digit_process(x):
    """
    transform number strings in form "12,300" & "12.5k" into real numbers, drop suffixes like ' followers'
    @param num: number needs to be formatted
    @return: real number strings
    """
    x = re.findall("([\d,]+) follower", x[0])[0]

    # e.g. 12.1k
    if ',' in x:
        x = x.replace(',', '')

    # k means 1000, we drop it and turn into real numbers
    # e.g. 12.1k
    if 'k' in x:
        x = x.replace('.', '')
        x = x.split('k')[0]
        x = int(x) * 10 ** 2  # since number has comma (,) we only need to multiply 100

    return str(x)


def rating_star_digit(text):
    """
    rating data in html source looks like '4 out of 5', i.e. 4 stars out of 5
    @param text: html tag rating data
    @return: number of stars given to this book
    """
    x = text.split(' out')[0]
    x = x.split(' ')[1]

    return x


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cookie': 'ccsid=159-7930093-9537415; __qca=P0-1361510703-1675140696151; __gads=ID=8bdee2b028f48ea8:T=1675140697:S=ALNI_Mb3T4yBV0keqM4ZYY1skkrpV5LzqQ; csm-sid=401-6433125-3410995; srb_8=0_ar; lc-main=en_US; ubid-main=135-5942988-0104347; allow_behavioral_targeting=true; likely_has_account=true; session-id=135-3887267-7214224; csm-hit=tb:J6642CY04B39AYBVQAZJ+s-J6642CY04B39AYBVQAZJ|1675150266411&t:1675150266411&adb:adblk_no; session-id-time=2305870289l; session-token=qvyFSX8xzfwdWlT60v9Djx5MAEJQ8VEJJaYKDGsCGZEyr45nQQTwnWvViAAZVA9JQJj3tDG7XqmQg7UKsm59Tuj7Ne7NkvvrMFtdLK3SszdZUbX2zCylk/vYVHBKrHoFS7fer0BaB8CHRlk7ldJ++Rh556CL1MvNNOexPQ6ewFIfvwM0zOlP0IPDN+XGBRk7ZauP3/4aMBUAiSAJAcJyTu2uhWcznuHOOP2UQtg7FO4AoEDvWRC2lEOSGJm5i/iv; x-main="aw?A0ryleOVNJR@Vp6S92fIrEyMqZm0dDvoPZ7jhDpu1TVA?Vx?HzTJQeZyi1Qvv"; at-main=Atza|IwEBIBxIPJLtzTaZW38PFjTVzr3ttEHVuPwy6-K--zUMmt5zAtLr5WYPu44qfkTXB1Huonli4DhJZw0K9JlBWvHfK3vIoLQ0DSPF3Scideb3INBS6U5lGt0QASZMNfrd_WlBZzHUslCxTca6x7fgn3Q6A95Kvyj61VUpKSiVUajjsyMaQ9fu8X4ZInenOQtMBavNG-OVx1_GJSHLbiFGRErqhuzg6v_nZMvi44W_nHnkWrJlN6ApCgqssTxwIi8MOFczHQY; sess-at-main="TS3W6kQt7Yo4f2bvbNpFbvKnCaY7w93Zjg1hpdnHkC0="; __gpi=UID=000009389ed92c0e:T=1675140697:RT=1677009295:S=ALNI_MZL02vjB6yrUntv62VbaO-O6V11Pg'
    }

    # start a request session
    session = requests.Session()

    # get genre names to loop over
    genre_names = os.listdir('./GoodReads')
    genre_names.remove('Book_Genres.csv')

    df_book = pd.read_csv('./GoodReads_stats/books_add.csv', encoding='unicode_escape')
    df_book.drop_duplicates(inplace=True)  # somtimes having duplicate books, causing error
    url_list = df_book['URL'].values  # get book URLs
    print(len(url_list))
    # create directory for storage of different kinds of files
    if not os.path.exists('./GoodReads_stats/basic_info'):
        os.mkdir('./GoodReads_stats/basic_info')

    if not os.path.exists('./GoodReads_stats/book_reviews'):
        os.mkdir('./GoodReads_stats/book_reviews')

    i = 2071
    for url in url_list[2071:]:
        print("Currently crawling the %d th book, URL: %s" % (i, url))
        page_text = session.get(url=url, headers=headers).text
        tree = etree.HTML(page_text)

        # book general information
        title = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[1]/div[1]/h1/text()')
        if not title:
            continue
        else:
            title = [''.join([i for i in title[0] if i not in punctuation])]  # drop irregular chars in title
        print("Current book is: ", title)

        overall_rate = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[2]'
                                  '/a/div[1]/div/text()')
        if not overall_rate:
            continue

        book_desc = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[1]'
                               '/div/div/span//text()')
        book_desc = [''.join(book_desc)]

        # genre tags apart from the main classification tag
        genres = []
        span_list = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[5]/ul/span[1]/span')
        for span in span_list[1:]:
            genres.extend(span.xpath('./a/span/text()'))

        if not genres:
            genres = ['N/A']

        page_num = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[6]/div/span[1]/span'
                              '/div/p[1]/text()')
        if not page_num:
            page_num = ['N/A']
        else:
            page_num = re.findall('([\d,]+) page', page_num[0])

        publish_date = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[6]/div/span[1]/span'
                                  '/div/p[2]/text()')
        if not publish_date:
            publish_date = ['N/A']
        elif 'Published' in publish_date[0]:
            publish_date = [publish_date[0].split('Published ')[1]]
        else:
            publish_date = [publish_date[0].split('published ')[1]]  # only retrieve date

        # Award attribute is tricky, it does not exist in the place that as the original html displays
        # I download the scraped html source to find it in somewhere else, and match it by RE
        award = tree.xpath('//*[@id="__NEXT_DATA__"]/text()')
        award = re.findall(r'Award","name":"(.*?)","webUrl', award[0])
        if not award:
            award = ['N/A']

        # book uid
        uid = re.findall('show/(\d+)[\.-]*', url)

        # author information
        author_name = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[8]/div[2]/div/div[1]'
                                 '/div[2]/div[1]/div[1]/h4/a/span/text()')
        if not author_name:
            continue

        book_num = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[8]/div[2]/div/div[1]'
                              '/div[2]/div[1]/div[1]/span/text()[1]')
        if not book_num:
            book_num = ['N/A']
        else:
            book_num = [book_num[0].replace(',', '')]

        follower_num = tree.xpath(
            '//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[8]/div[2]/div/div[1]/div[2]/div[1]/div[1]/span/span/text()[1]')
        if not follower_num:
            follower_num = ['N/A']
        else:
            follower_num = [follower_num[0].replace(',', '')]

        author_desc = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[8]/div[3]/div[1]/div'
                                 '/div/span//text()')
        author_desc = [''.join(author_desc)]

        # book rating & review information
        rating_num = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[2]/a/div[2]/div/span[1]'
                                '/text()[1]')
        if not rating_num:
            rating_num = ['N/A']
        else:
            rating_num = [rating_num[0].replace(',', '')]

        review_num = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[2]/a/div[2]/div/'
                                'span[2]/text()[1]')
        if not review_num:
            continue
        else:
            review_num = [review_num[0].replace(',', '')]

        # rating distribution (5 star: xxx, 4 star: xxx, etc.)
        rating_dist = []
        rating_div = tree.xpath('//*[@id="ReviewsSection"]/div[4]/div[1]/div[2]/div/div')
        for div in rating_div:
            dist = div.xpath('./div[3]/text()')[0].replace(',', '')
            rating_dist.append(dist)
        rating_dist = [rating_dist]

        # try to store book info, but if occurring error, jump to next one
        # we have no time to consider every book's specific bug case-by-case
        try:
            basic_df = pd.DataFrame({'Uid': uid,
                                     'Title': title,
                                     'Author': author_name,
                                     'Genre': [genres],
                                     'Rate': overall_rate,
                                     'Publish_Date': publish_date,
                                     'Page_Num': page_num,
                                     'Award': [award],
                                     'Description': book_desc,
                                     'Author_Desc': author_desc,
                                     'Book_Authored': book_num,
                                     'Follower_Num': follower_num,
                                     'Review_Num': review_num,
                                     'Rating_Num': rating_num,
                                     'Rating_Dist:': rating_dist
                                     })
            basic_df.to_csv('./GoodReads_stats/basic_info/' + title[0] + '_info.csv', index=False)
            print("Book basic information scraped successfully!")

        except ValueError:
            print('Unmatched arrays length, skip')  # common error is some missing information in some specific tags
            i += 1
            continue

        '''
        retrieve reviews for each book
        '''
        book_uid = []
        book_title = []
        reviewer_name = []
        n_review = []
        n_follower = []
        review_rate = []
        review_date = []
        review_content = []
        n_likes = []
        n_comments = []

        # html tags list to loop
        review_divs = tree.xpath('//*[@id="ReviewsSection"]/div[5]/div[2]/div')

        j = 1  # indicator to count # usable comment records
        for div in review_divs:
            # due to large source, we only retrieve 15 usable comments data for each book
            if j > 15:
                break

            # book reviews
            reviewer_name_temp = div.xpath('./article/div/div/section[2]/span[1]/div/a/text()')

            # sometimes we have website ads, pass it
            if not reviewer_name_temp:
                print("Website Ads, pass")
                continue

            content = div.xpath('./article/section/section[2]/section/div/div[1]/span//text()')
            content = ''.join(content)

            if not content:
                continue

            # use langdetect package to filter non-english comments
            try:
                if detect(content) != 'en':
                    continue
            except:
                continue

            n_review_temp = div.xpath('./article/div/div/section[2]/span[2]/div/span[1]/text()')
            if not n_review_temp:
                continue

            n_follower_temp = div.xpath('./article/div/div/section[2]/span[2]/div/span[2]/span/text()')
            if not n_follower_temp:
                continue

            review_rate_temp = div.xpath('./article/section/section[1]/div/span/@aria-label')
            if not review_rate_temp:
                continue

            review_date_temp = div.xpath('./article/section/section[1]/span/a/text()')
            if not review_date_temp:
                continue

            # store in a list
            reviewer_name.extend(reviewer_name_temp)
            review_content.append(''.join(content))
            n_review.extend(re.findall('([\d,]+) review', n_review_temp[0]))
            n_follower.append(digit_process(n_follower_temp[0]))
            review_rate.extend(rating_star_digit(review_rate_temp[0]))
            review_date.append(''.join(review_date_temp))

            n_likes_temp = div.xpath('./article/section/footer/div[1]/div[1]/button/span/text()')
            if not n_likes_temp:
                n_likes.extend(['N/A'])
            else:
                n_likes.append(n_likes_temp[0].split(' likes')[0])

            n_comments_temp = div.xpath('./article/section/footer/div[1]/div[2]/button/span/text()')
            if not n_comments_temp:
                n_comments.extend(['N/A'])
            else:
                n_comments.append(n_comments_temp[0].split(' comments')[0])

            book_uid.append(uid[0])
            book_title.extend(title)
            j += 1

        # try to store book reviews as csv files
        try:
            review_df = pd.DataFrame({'Uid': book_uid,
                                      'Title': book_title,
                                      'Reviewer': reviewer_name,
                                      'N_Review': n_review,
                                      'N_Follower': n_follower,
                                      'Review_Rate': review_rate,
                                      'Review_Date': review_date,
                                      'Content': review_content,
                                      'N_Likes': n_likes,
                                      'N_Comments': n_comments})

            review_df.to_csv('./GoodReads_stats/book_reviews/' + title[0] + '_reviews.csv', index=False)
            print("Book reviews scraped successfully!")

        except ValueError:
            print('Unmatched arrays length, skip')
            os.remove('./GoodReads_stats/basic_info/' + title[0] + '_info.csv')
            i += 1
            continue

        # retrieve book statistics
        stats_url = 'https://www.goodreads.com/book/stats/' + uid[0]
        try:
            book_stats(session=session, headers=headers, uid=uid[0])
            print("Book statistics scraped successfully! Jump to next book")
            print("---------------------------------------------------------")
            i += 1

        except IndexError:
            print("Re-crawl book statistics")
            book_stats(session=session, headers=headers, uid=uid[0])
            print("Success! Jump to next book")
            i += 1

