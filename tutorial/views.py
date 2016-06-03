from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import pycurl
import json
import pyorient

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

class TutorialViews:
    def __init__(self, request):
        self.request = request

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
        for pair in pairs:
            doc1=pair["doc1"]
            doc2=pair["doc2"]
            buffer = BytesIO()
            c = pycurl.Curl();
            url="http://localhost:9200/hello_world_example/_search?q=_id:"+doc1
            c.setopt(pycurl.URL, url)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()

            body = buffer.getvalue()
            id_hit=json.loads(body)
            search_text=id_hit["hits"]["hits"][0]["_source"]["text"]

            #Second request to elastic to get score
            data_object={"query" : {"filtered" : {"filter" : {"match" : {"_id" : doc2}},"query" : {"match" : {"text" : search_text}}}}}
            data=json.dumps(data_object)

            buffer = BytesIO()
            second_url="http://localhost:9200/hello_world_example/_search"
            c=pycurl.Curl()
            c.setopt(pycurl.URL, second_url)
            c.setopt(pycurl.POSTFIELDS, data)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()
            c.close()
            body = buffer.getvalue()
            #print(body)
            text_hit=json.loads(body)
            if text_hit["hits"]["total"] == 0:
                pair["score"]=0
            else:
                pair["score"]=text_hit["hits"]["hits"][0]["_score"]
        self.log_scores(pairs)


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
        pairs=self.get_pairs()
        self.scoring_function(pairs)
        return Response(
            content_type='text/plain',
            body="Hello scorer \n"
        )
