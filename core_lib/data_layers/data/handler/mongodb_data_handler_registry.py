import pymongo


class MongoDBDataHandlerRegistry:

    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.my_db
    dblist = db.test_collection
    print(dblist)


mongo = MongoDBDataHandlerRegistry()
