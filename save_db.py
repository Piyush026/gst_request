from pymongo import MongoClient
import urllib.parse


url = "mongodb+srv://polo:" + urllib.parse.quote(
    "gvhjgv3456nb") + "@cluster0.b8rq1.mongodb.net/test?retryWrites=true&w=majority"
# url is just an example (your url will be different)

cluster = MongoClient(url)
db = cluster['scraper10']
collection = db['gst2']


def insertData(pst1):
    try:
        collection.insert_one(pst1)
        print("data inserted")
    except Exception as e:
        print(e)
