import numpy as np
import pandas as pd
from langdetect import detect
from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer, PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from rake_nltk import Rake
from scipy import sparse


def detect_language(phrase):
    """
    Test function for language detection!
    """
    language_dict = {'en': 'english', 'fr': 'french', 'de': 'german', 'it': 'italian'}
    try:
        lang = language_dict[detect(phrase)]
    except:
        lang = 'english'
    return lang

# TODO: Safe delete the function ranking_tfidf
def ranking_tfidf(text, out_dataframe=False):
    """
    Testing fuction to create a TFIDF score (requires to download the nltk data packages!)
    ** Formula: score(D, T) = termFrequency(D, T) * log(N / docFrequency(T))
    ** Automatic detection of the language
    ** Return momentarily a tuple [(word, TFIDF score)],   or a pandas dataframe
    """
    # Detect the language of the text
    lang = detect_language(text)
    # Tokenize the text into sentences
    sentences = sent_tokenize(text, language=lang)

    # Tokenize each sentence into words
    words = [word_tokenize(sentence, language=lang) for sentence in sentences]

    # Remove stop words and perform stemming to normalize the text
    stop_words = set(stopwords.words(lang))
    stemmer = PorterStemmer()
    words = [[stemmer.stem(word.lower())
        for word in sentence if word.lower() not in stop_words] for sentence in words]

    # Calculate the TF-IDF (improvement with BM25 possible) score for each sentence to rank them
    vectorizer = TfidfVectorizer()
    vect = vectorizer.fit_transform([" ".join(sentence) for sentence in words])

    # Rank the words based on their TF-IDF scores
    scores = zip(vectorizer.get_feature_names_out(),
                 np.around(np.asarray(vect.sum(axis=0)).ravel(), decimals=2))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    df_ranking = pd.DataFrame(sorted_scores, columns=['word', 'tfidf'])

    if out_dataframe:
        return df_ranking
    else:
        return (sorted_scores, lang)




class TFIDF_BM25():
    def __init__(self, b=0.75, k1=1.6, avd1=0.1):
        self.vectorizer = TfidfVectorizer(norm=None, smooth_idf=False)
        self.b = b
        self.k1 = k1
        self.avd1 = avd1
        self.abstracts = []

    # TODO: Improve loop efficiency in the cleansing_ranking function
    # WARNING The stemming and cleansing process is computationally expensive! (1421 lines in 36 s)
    # TODO: We could integrate the cleaned results into the data with an additional column "keywords+"
    def cleansing_ranking(self, texts):
        """
        texts is a pandas DF with at least a non empty "ABSTRACT" column
        """
        self.results = []
        self.index = texts.index.values
        for text in texts['ABSTRACT'].values.tolist():
            ranker = TfidfVectorizer(norm='l2')
            sentences = sent_tokenize(text, language=detect_language(text))
            sentence_cleaned = []
            for sentence in sentences:
                lang = detect_language(sentence)
                stemmer = SnowballStemmer(lang)
                words = (word_tokenize(sentence, language= lang))
                stop_words = stopwords.words(detect_language(sentence))
                words_cleaned = []
                for word in words:
                    if word.lower() not in stop_words and word.lower() not in list(punctuation):
                        words_cleaned.append(stemmer.stem(word.lower()))
                sentence_cleaned.append(words_cleaned)
            vector = ranker.fit_transform([' '.join(words) for words in sentence_cleaned])
            scores = zip(ranker.get_feature_names_out(),
                        np.around(np.asarray(vector.sum(axis=0)).ravel(), decimals=2))
            self.results.append(pd.DataFrame(sorted(scores, key=lambda x: x[1], reverse=True), columns=['word', 'tfidf']))
        return self.results # REMOVE?
    
    def fit(self, texts):
        """
        Texts is a list of pandas from cleansing_ranking.
        """
        self.abstracts = [' '.join(abstract['word'].tolist()) for abstract in texts]
        self.vectorizer.fit(self.abstracts)
        score = super(TfidfVectorizer, self.vectorizer).transform(self.abstracts)
        self.avd1 = score.sum(1).mean()
    
    def transform(self, q):
        """
        q is a str with a query (single word or multiple words)
        """
        document = super(TfidfVectorizer, self.vectorizer).transform(self.abstracts)
        doc_lenght = document.sum(1).A1

        query, = super(TfidfVectorizer, self.vectorizer).transform([q])
        assert sparse.isspmatrix_csr(query)

        document = document.tocsc()[:, query.indices]
        denom = document + (self.k1 * (1 - self.b + self.b * doc_lenght / self.avd1))[:, None]
        idf = self.vectorizer._tfidf.idf_[None, query.indices] - 1.
        numer = document.multiply(np.broadcast_to(idf, document.shape)) * (self.k1 + 1)
        return (numer / denom).sum(1).A1