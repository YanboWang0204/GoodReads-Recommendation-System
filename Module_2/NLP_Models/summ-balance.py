import numpy as np
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/paraphrase-mpnet-base-v2')
from LexRank import degree_centrality_scores
from tqdm import tqdm
import pandas as pd
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import numpy as np
import timeout_decorator

df_reviews = pd.read_csv('data/Book_reviews_cleaned.csv')

book_dict = {}
for index, row in tqdm(df_reviews.iterrows()):
    key = row['Uid']
    if key not in book_dict:
        comments = ' '
        comments += row['Content']
        book_dict[key] = comments
    else:
        book_dict[key] += row['Content']

df_comments = pd.DataFrame.from_dict(book_dict, orient='index', columns=['Content'])

def get_document_stats(Uid):
    # select sample review sentences
    sentences = sent_tokenize(df_comments.loc[Uid].Content)
    sentiments = list(map(lambda text: TextBlob(text).sentiment.polarity, sentences))
    doc_sentiment = np.mean(sentiments)
    return doc_sentiment

@timeout_decorator.timeout(5)
def extract_summary(Uid, topk=5):

    """

    :param Uid:
    :param topk:
    :return: out_summary: summary string separated by [SEP]
            out_sentiment: sentiments string separated by [SEP]
            out_centralities: centrality score string separated by [SEP]
            mean_sentiment,
            mean_centrality,
            mean_redundancy,
            doc_sentiment: mean sentiment of original text score
    """

    # select sample review sentences
    sentences = sent_tokenize(df_comments.loc[Uid].Content)
    # we calculate the sentiment score using TextBlob, this measurement will be used as n evaluation metric
    sentiments = list(map(lambda text: TextBlob(text).sentiment.polarity, sentences))
    doc_sentiment = np.mean(sentiments)

    # Encode each sentence with Sentence-BERT
    sentence_embeddings = model.encode(sentences)
    # Calculate the cosine similarity scores among sentences
    cos_scores = util.cos_sim(sentence_embeddings, sentence_embeddings).numpy()
    # Obtain the centrality scores with LexRank
    centrality_scores = degree_centrality_scores(cos_scores, threshold=None)

    # We use redundancy score as another evaluation metric
    def _compute_redundancy(idx, summary_idxes):
        if not summary_idxes: return 0
        return max([cos_scores[idx][senti] for senti in summary_idxes])

    # We compute the sentiment score difference between the extracted summary and the original review text
    def _sentiment_difference(idx, summary_idxes):
        return abs(doc_sentiment - np.mean([sentiments[idx]] + [sentiments[senti] for senti in summary_idxes]))

    summary_idxes = []
    best_idx = None

    while len(summary_idxes) < topk and best_idx != -1:
        best_idx, best_objective = -1, -1000
        for idx in range(len(sentences)):
            if idx not in summary_idxes:
                redundancy = _compute_redundancy(idx, summary_idxes)
                sentiment_difference = _sentiment_difference(idx, summary_idxes)
                # maximizing centrality while minimizing redundancy and sentiment difference
                objective = centrality_scores[idx] - redundancy - sentiment_difference
                if objective > best_objective:
                    best_idx = idx
                    best_objective = objective
        if best_idx != -1:
            summary_idxes.append(best_idx)

    # Store the outputs
    out_summary = ""
    out_sentiment = ""
    out_centralities = ""
    summary_sentiments = []
    summary_centralities = []
    summary_redundancies = []

    for idx in summary_idxes:
        summary_sentiments.append(sentiments[idx])
        summary_centralities.append(centrality_scores[idx])

        # compute redundancy of the specific sentence to all other sentences in the summary
        summary_idxes.remove(idx)
        redundancy = _compute_redundancy(idx, summary_idxes)
        summary_idxes.append(idx)
        summary_redundancies.append(redundancy)

        out_summary += sentences[idx] + "[SEP]"
        out_sentiment += str(sentiments[idx]) + "[SEP]"
        out_centralities += str(centrality_scores[idx]) + "[SEP]"

    mean_sentiment = np.mean(summary_sentiments)
    mean_centrality = np.mean(summary_centralities)
    mean_redundancy = np.mean(summary_redundancies)

    print(f"{mean_sentiment}, {mean_centrality}, {mean_redundancy}, {doc_sentiment}")

    return out_summary, out_sentiment, out_centralities, mean_sentiment, mean_centrality, mean_redundancy, doc_sentiment


# store output in pandas dataframe
Uids = list(book_dict.keys())
summaries = []
sentiments = []
centralities = []
mean_sentiments = []
mean_centralities = []
mean_redundancies = []
doc_sentiments = []

for uid in tqdm(Uids):
    try:
        out_summary, out_sentiment, out_centralities, mean_sentiment, mean_centrality, mean_redundancy, doc_sentiment = extract_summary(uid)
        summaries.append(out_summary)
        sentiments.append(out_sentiment)
        centralities.append(out_centralities)
        mean_sentiments.append(mean_sentiment)
        mean_centralities.append(mean_centrality)
        mean_redundancies.append(mean_redundancy)
        doc_sentiments.append(doc_sentiment)
    except:
        pass

out_df = pd.DataFrame(list(zip(Uids, summaries, sentiments, centralities, mean_sentiments, mean_centralities, mean_redundancies, doc_sentiments)), columns = ['Uid', 'Summary', 'Sentiment', 'Centrality', 'Mean_sentiment', 'Mean_centrality', 'Mean_redundancy', 'doc_sentiment'])

print(out_df.head())

out_df.to_csv("output-df/summ3_v2.csv")

print("successfully store data frame")
