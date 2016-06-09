from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
#import pycurl
import json
import pyorient
#from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from swalign_doc import swalign_doc


try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

class TutorialViews:
    def __init__(self, request):
        self.request = request
'''
    def get_db_client(self):
        db_name = "ElasticLogs"
        client = pyorient.OrientDB("localhost", 2424)
        cluster_info = client.db_open( db_name, "admin", "admin" )
        return client

    def log_scores(self,pairs):
        #print(pairs)
        print("logging scores now")
        client=self.get_db_client()
        for pair in pairs:
            #print(pair)
            #print("insert into DocumentSimilarityLog ( doc_pair_id, score) values ("pair.doc_pair_id","pair.score)")
            query=""
            query+="insert into DocumentSimilarityLog ( doc_pair_id, score) values ("
            query+= str(pair["doc_pair_id"])
            query+=","
            query+= str(pair["score"])
            query+=")"
            #print(query)
            result = client.command(query)



    def get_pairs(self):
        client=self.get_db_client()
        result = client.query("select from DocumentPair")
        docs=[]
        for row in result:
            docs.append({"doc_pair_id":row.doc_pair_id, "doc1": row.doc1, "doc2":row.doc2 })
        return docs



    def scoring_function(self, pairs):
        #for pair in pairs:
        pair=pairs[0]
        doc1=pair["doc1"]
        doc2=pair["doc2"]
        client = Elasticsearch()
        s = Search(using=client, index="hello_world_example").query("match", _id=doc1)
        response=s.execute()
        search_text=response[0]["text"]
        #search_text=response["hits"]["hits"][0]["_source"]["text"]
        #print(search_text)

        #Second request to elastic to get score
        s = Search(using=client, index="hello_world_example").query("match", text=search_text)
        response=s.execute()
        for hit in response:
            #print(hit.meta.score, hit.text)
            #print(match)
            #search_text=match["text"]
            print(match["text"], match["_score"])
        #self.log_scores(pairs)
'''
    #call elastic search for candidate docs
    def find_candidate_documents(self, search_doc):
        #print(search_doc)
        client = Elasticsearch()
        s = Search(using=client, index="hello_world_example").query("match", text=search_doc)
        response=s.execute()

        new_response=[]
        for hit in response:
            #print(hit.meta.id,hit.meta.score, hit.text)
            new_response.append({"id":hit.meta.id, "score":hit.meta.score, "text": hit.text})
        return new_response

    #min-max normalization of bm25 scores
    def normalize_score(self, candidate_docs):
        max_score=candidate_docs[0]["score"]
        min_score=candidate_docs[-1]["score"]
        for hit in candidate_docs:
            hit["score"] = (hit["score"] - min_score)/(max_score - min_score)
        #print(candidate_docs)

    #apply smith-watterman on documents
    def get_alignment_score(self, search_doc, candidate_docs):
        sd= swalign_doc()
        max_alignment_score=sd.get_alignment_score(search_doc, search_doc)
        min_alignment_score= 0;
        for hit in candidate_docs:
            hit["sw_score"]=sd.get_alignment_score(search_doc, hit["text"])
            #normalize allignment scores
            hit["sw_score"]=(hit["sw_score"] - min_alignment_score)/(max_alignment_score- min_alignment_score)
        #print(candidate_docs)

    #take weighted average bm25 and sw scores
    def get_final_scores(self, candidate_docs):
        for hit  in candidate_docs:
            hit["_score"] = (0.5 * hit["score"]) + (0.5 * hit["sw_score"])
            del hit["score"]
            del hit["sw_score"]

    @view_config(route_name='home')
    def home(self):
        return HTTPFound(location='/plain')

    @view_config(route_name='plain')
    def plain(self):
        name = self.request.params.get('name', 'No Name Provided')

        body = 'URL %s with name: %s' % (self.request.url, name)
        return Response(
            content_type='text/plain',
            body=body
        )


    @view_config(route_name='score')
    def score(self):
        request_body=self.request.json_body
        search_text= request_body["search_text"]
        candidate_docs= self.find_candidate_documents(search_text)
        self.normalize_score(candidate_docs)
        self.get_alignment_score(search_text, candidate_docs)
        self.get_final_scores(candidate_docs)
        body= json.dumps(candidate_docs)
        #print(candidate_docs)
        return Response(
            content_type='text/plain',
            body=body
        )
