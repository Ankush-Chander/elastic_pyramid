from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import pycurl
import json

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

class TutorialViews:
    def __init__(self, request):
        self.request = request

    def scoring_function(pairs):
        print(pairs)


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
        reqobject=self.request.json_body
        doc1=reqobject["pairs"][0]["doc1"]
        doc2=reqobject["pairs"][0]["doc2"]
        #scoring_function(reqobject["pairs"])
        buffer = BytesIO()
        c = pycurl.Curl();
        url="http://localhost:9200/hello_world_example/_search?q=_id:"+doc1
        c.setopt(pycurl.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        #print(c.getinfo(c.RESPONSE_CODE))
        #c.close()

        body = buffer.getvalue()
        # Decode using the encoding we figured out.
        id_hit=json.loads(body)
        print(type(id_hit["hits"]["hits"]))
        print(id_hit["hits"]["hits"][0]["_source"]["text"])
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
        body = buffer.getvalue()
        #print(body)
        text_hit=json.loads(body)
        print(text_hit["hits"]["hits"][0]["_score"])
        #print(text_hit["hits"]["hits"][0]["_source"]["text"])
        c.close()
        return Response(
            content_type='text/plain',
            body="Hello scorer \n"
        )

        '''name = self.request.params.get('name', 'No Name Provided')

        body = 'URL %s with name: %s' % (self.request.url, name)
        return Response(
            content_type='text/plain',
            body=body
        )'''
