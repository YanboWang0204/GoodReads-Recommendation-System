"""
INDENG 243 - Analytics Lab (Spring 2023)
@Project: GoodReads: Book Analytics & Recommendation System
@Group: 18
@Author: Yanbo Wang
@Email: yanbo.wang@berkeley.edu

The following are the main codes I used to scrape data from GoodReads.
"""

import requests
import os
from lxml import etree
import pandas as pd
import numpy as np
import time
import re
from langdetect import detect  # package for filtering non-English reviews
from string import punctuation


def book_genre(headers):
    """
    scrape book genres with URLs and store as a csv file
    @param headers:
    @return: book genre and corresponding urls
    """
    if os.path.exists('./GoodReads/Book_Genres.csv'):
        print("You have already scraped book genres")
    else:
        category_url = 'https://www.goodreads.com/genres'
        page_category = requests.get(url=category_url, headers=headers).text
        tree = etree.HTML(page_category)
        div_list = tree.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div/div')

        format_url = 'https://www.goodreads.com%s'
        genre_list = []
        url_list = []

        # retrieve information from HTML tags
        for div in div_list[:2]:
            a_list = div.xpath('./a')
            for a in a_list:
                genre_list.append(a.xpath('./text()')[0])  # genre names
                url_list.append(format(format_url % a.xpath('./@href')[0]))  # corresponding URLs

        # store in a dataframe for repeated use
        df = pd.DataFrame({'Genre': genre_list,
                           'URL': url_list})
        df.to_csv('./GoodReads/Book_Genres.csv', index=False)

    pass


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


def genre_book_list(session, headers, page=7):
    """
    retrieve genre book list
    @param session: request session object
    @param headers: session headers
    @param page: number of pages in each genre to crawl
    @return: save as a csv file containing book title and corresponding urls for each genre
    """

    if os.path.exists('./GoodReads/young-adult/books_url.csv'):
        print("You have already scraped all book URLs for each genre")
    else:
        # read genres csv & modify to urls for further scraping
        df_genre = pd.read_csv('./GoodReads/Book_Genres.csv')
        df_genre['URL'] = df_genre['URL'].apply(lambda url: url.replace('genres', 'shelf/show') + '?page=%d')
        df_genre['Genre'] = df_genre['Genre'].apply(genre_name_modify)
        # print(df_genre)

        # iterate over each genre, retrieve first n pages of books (n = page - 1)
        for index, row in df_genre.iterrows():
            genre = row['Genre']
            url = row['URL']

            if not os.path.exists('./GoodReads/' + genre):
                os.mkdir('./GoodReads/' + genre)

            if os.path.exists('./GoodReads/' + genre + '/books_url.csv'):  # already scraped
                df = pd.read_csv('./GoodReads/' + genre + '/books_url.csv')
                if len(df) == 50 * (page - 1):  # avoid cases when not scraped enough books wanted
                    continue

            book_title = []
            book_url = []

            time.sleep(np.random.randint(1, 4))

            # retrieve defined page numbers, each page contains 50 books
            for pageNum in range(1, page):
                time.sleep(np.random.randint(1, 3))
                print("Current Genre is: " + genre + ", Page is: " + str(pageNum))
                page_book = session.get(url=format(url % pageNum), headers=headers).text
                tree = etree.HTML(page_book)
                div_list = tree.xpath('/html/body/div[2]/div[3]/div[1]/div[2]/div[3]/div[@class="elementList"]')

                for div in div_list:
                    book_title.append(div.xpath('./div[1]/a/@title')[0])
                    book_url.append('https://www.goodreads.com' + div.xpath('./div[1]/a/@href')[0])

            # store book titles & corresponding URLs under current genre
            df_book = pd.DataFrame({'Title': book_title,
                                    'URL': book_url})
            df_book.to_csv('./GoodReads/' + genre + '/books_url.csv', index=False)

    pass


def book_stats(session, headers, url, genre, book_name):
    """
    retrieve current book's statistics data
    @param session: current request session
    @param headers: session headers
    @param url: current book's statistic url
    @param genre: current book's genre belonging to
    @param book_name: current book's name

    @return: store book stats as a csv file
    """
    if not os.path.exists('./GoodReads/' + genre + '/stats'):
        os.mkdir('./GoodReads/' + genre + '/stats')

    page_stats = session.get(url=url, headers=headers).text
    tree = etree.HTML(page_stats)
    tr_list = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[2]/div[5]/table/tr')

    stats_list = []
    # data starting from the third tr tag
    for tr in tr_list[2:-1]:
        stats_list.append(tr.xpath('./td/text()'))

    stats_df = pd.DataFrame(data=stats_list, columns=['date', 'added', 'ratings', 'reviews', 'to-read'])
    stats_df.to_csv('./GoodReads/' + genre + '/stats/' + book_name + '_stats.csv', index=False)

    pass


def digit_process(num):
    """
    transform number strings in form "12,300" & "12.5k" into real numbers, drop suffixes like ' followers'
    @param num: number needs to be formatted
    @return: real number strings
    """
    x = num.split(' followers')[0]

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
    print("Hello, welcome to use my web crawler code to scrape information from GoodReads.com")
    print()
    print("Please make sure you have registered an account on GoodReads.com, "
          "we will use your web cookies for further scraping.")

    # create main folder for storing scraped files
    if not os.path.exists('./GoodReads'):
        print("Setting up folder 'GoodReads' for files storage")
        os.mkdir('./GoodReads')

    # Guideline prompts
    print("---------------------------------------------------------")
    print("Please input your browser user agent & website cookies:")
    print()
    print("To find this information, please try this website 'https://www.goodreads.com/book/stats/84981'")
    print("Press F12 -> Network -> find '84981' under name -> Headers -> Request Headers -> Cookie & User-Agent")
    print("*** If you only see the login page, that means you have not registered an account, please do so. ***")

    # Accept user information from input
    print("---------------------------------------------------------")
    print("Please copy and paste information after following prompts:")
    UA = input("User-Agent: ")
    cookie = input("Cookie: ")

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    #     'Cookie': 'ccsid=513-4691043-0078794; __qca=P0-68425638-1674878204802; __gads=ID=a371dbbc63ae716b:T=1674878205:S=ALNI_MYkuLwRIDAXts5JGpQioSlHOUvkFQ; __gpi=UID=0000093711720843:T=1674878205:RT=1676003254:S=ALNI_MY8KPOmyp-2kTWHKUG4r7NgbZydPw; csm-sid=462-0242494-7172375; srb_8=0_ar; session-id=138-3694462-7458309; session-id-time=2306723268l; lc-main=en_US; csm-hit=tb:40EN54EXM1MKH7V5AT1X+s-7Q04HP2KCC55YE8Z1ED7|1676003272510&t:1676003272510&adb:adblk_no; ubid-main=133-4102551-3356951; likely_has_account=true; allow_beha…wy9BC3Awco3cOS/XDqZHohibvfJKB/6AE42PPuqv+OL4MapkzHUhTFf7ZNE6QQWGXplZVanAzC3yFYGTYCeKB+MVMFeKEUSm8; x-main="lmz39xJhS7vXjvXYej8QtXwRdLk0k6Fvb@?kUqR1EFkLkjm2qBhFUOGFTCtJYK4g"; at-main=Atza|IwEBIJ3DK-R3_tFfaqB-rvKcEv2lzHVtGBa5K9dqP52M0aUgeQTB-1yAjBZJgarHl7uqu-rUsPqSjX2nPWUh_tYUbnV9HbnO9wYWoGM_wf4J58_JTAGjqcP6T52q0CPCTDlG4K2--TjU712oCUb8AgmN-xC83FmOwAeqDsSzz5IMBGqZ56bECGoWkJg-sO9hTZAbA23p-Zdi8lYJ_JMjmtbov3G9rau5bRkCHrCyqPLsZXnLNBH0KtbG34JxZfyOVmoO170; sess-at-main="z9Io9eA4lfYebMZjCQzMVQcl8OdZvk3IeqcdjvDIsiw="'
    # }

    headers = {
        'User-Agent': UA,
        'Cookie': cookie
    }

    # start a request session
    session = requests.Session()

    # retrieve book categories
    book_genre(headers=headers)

    # retrieve book titles & URLs under different genres
    genre_book_list(session=session, headers=headers, page=7)

    # get genre names to loop over
    genre_names = os.listdir('./GoodReads')
    genre_names.remove('Book_Genres.csv')

    '''
    Starting from each Genre -> Book list under each genre -> Retrieve each book's info & reviews & statistics
    '''
    for genre in genre_names:
        time.sleep(np.random.randint(3, 6))

        # first get book lists under current genre
        path = './GoodReads/' + genre + '/books_url.csv'
        df_book = pd.read_csv(path)
        df_book.drop_duplicates(inplace=True)  # somtimes having duplicate books, causing error
        url_list = df_book['URL'].values  # get book URLs

        # create directory for storage of different kinds of files
        if not os.path.exists('./GoodReads/' + genre + '/basic_info'):
            os.mkdir('./GoodReads/' + genre + '/basic_info')

        if not os.path.exists('./GoodReads/' + genre + '/book_reviews'):
            os.mkdir('./GoodReads/' + genre + '/book_reviews')

        '''
        Loop over book URLs to retrieve each book's detailed data under this genre
        '''
        for url in url_list:
            # set index indicator
            i = np.where(url_list == url)[0]
            print("Currently crawling category (%s) the %d th book" % (genre, i))
            time.sleep(np.random.randint(2, 5))

            print("Current URL is: ", url)
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
            sub_genre = []
            span_list = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[5]/ul/span[1]/span')
            for span in span_list[2:]:
                sub_genre.extend(span.xpath('./a/span/text()'))

            if not sub_genre:
                sub_genre = ['N/A']

            page_num = tree.xpath('//*[@id="__next"]/div/main/div[1]/div[2]/div[1]/div[2]/div[6]/div/span[1]/span'
                                  '/div/p[1]/text()')
            if not page_num:
                page_num = ['N/A']
            else:
                page_num = re.findall('[\d]+', page_num[0])

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

            # book statistics
            uid = re.findall('\d+', url)

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
                                         'Genre': [genre],
                                         'Sub_Genres': [sub_genre],
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
                basic_df.to_csv('./GoodReads/' + genre + '/basic_info/' + title[0] + '_info.csv', index=False)
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
                n_review.extend(re.findall('[\d,?]+', n_review_temp[0]))
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

                review_df.to_csv('./GoodReads/' + genre + '/book_reviews/' + title[0] + '_reviews.csv', index=False)
                print("Book reviews scraped successfully!")

            except ValueError:
                print('Unmatched arrays length, skip')
                os.remove('./GoodReads/' + genre + '/basic_info/' + title[0] + '_info.csv')
                continue

            time.sleep(np.random.randint(1, 3))

            # retrieve book statistics
            stats_url = 'https://www.goodreads.com/book/stats/' + uid[0]
            book_stats(session=session, headers=headers, url=stats_url, genre=genre, book_name=title[0])
            print("Book statistics scraped successfully! Jump to next book")
            print("---------------------------------------------------------")
