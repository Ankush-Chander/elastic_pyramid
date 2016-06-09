import re
from nltk.corpus import stopwords
import numpy as np
#from swalign_doc import swalign_doc

class swalign_doc:

    def __init__(self, match_score=2, mismatch_score=-1, gap_penalty=-1, remove_stopwords=True):
        """ Create a new point at the origin """

        self.match_score= match_score
        self.mismatch_score = mismatch_score
        self.gap_penalty = gap_penalty
        self.remove_stopwords= remove_stopwords


    def doc_to_wordlist( self, doc ):
        # Function to convert a document to a sequence of words,
        # optionally removing stop words.  Returns a list of words.
        #
        # 1. Remove non-letters
        doc_text = re.sub("[^a-zA-Z]"," ", doc)
        #
        # 2. Convert words to lower case and split them
        words = doc_text.lower().split()
        #
        # 3. Optionally remove stop words (true by default)
        if self.remove_stopwords:
            stops = set(stopwords.words("english"))
            words = [w for w in words if not w in stops]
        #
        # 5. Return a list of words
        return(words)



    def similarity_function(self, word1, word2):
        if word1==word2:
            return True
        else:
            return False

    def max_of_two(self, a, b):
        if a>=b:
            return a
        else:
            return b

    def max_of_three(self, a, b, c):
        if a>=b and a>=c:
            return a
        elif b>=a and b>=c:
            return b
        else:
            return c

    def get_alignment_score(self, doc1, doc2):

        doc1= self.doc_to_wordlist(doc1)
        doc2= self.doc_to_wordlist(doc2)

        #print doc1
        #print doc2

        doc1=np.array(doc1)
        doc2=np.array(doc2)

        #initialize matrix
        rows=len(doc2)+1
        cols=len(doc1)+1
        max_row_value = np.zeros(rows)
        max_col_value = np.zeros(cols)
        max_sim_score_matrix= np.zeros((rows, cols))
        #print(max_sim_score_matrix)


        #print(rows, cols)
        for i in range(rows):
            for j in range(cols):
                if i==0 or j==0:
                    #print(i,j)
                    max_sim_score_matrix[i][j]=0
                else:
                    #print(i,j)
                    #print(doc1[i-1], doc2[j-1])

                    if self.similarity_function(doc1[j-1],doc2[i-1]):
                        max_sim_score_matrix[i][j]= max_sim_score_matrix[i-1][j-1] + self.match_score
                        #print (doc1[j-1], doc2[i-1], "match")
                        max_col_value[j] = self.max_of_two(max_col_value[j], max_sim_score_matrix[i][j])
                        max_row_value[i]= self.max_of_two(max_row_value[i], max_sim_score_matrix[i][j])
                        #print (doc1[j-1], doc2[i-1], "match", max_sim_score_matrix[i][j])
                    else:
                        #print (doc1[j-1], doc2[i-1], "mismatch")
                        max_sim_score_matrix[i][j]= self.max_of_three(max_sim_score_matrix[i-1][j-1] + self.mismatch_score,  max_col_value[j] + self.gap_penalty, max_row_value[i] + self.gap_penalty  )
                        max_sim_score_matrix[i][j]= self.max_of_two(0, max_sim_score_matrix[i][j])

        return max_sim_score_matrix[rows-1][cols-1]
                #similarity_function(doc1[i], doc2[j])
