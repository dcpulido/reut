import json
import logging
from bson import ObjectId
from pymongo import MongoClient

class MongoDAO:
    def __init__(self):
        self.client = MongoClient()

    def insert(self,
               ob,
               collection,
               instance=False):
        db = eval("self.client."+collection)
        if instance:
            ob = ob.to_dict()
        return db.ob.insert_one(ob)

    def get_by_arg(self,
                   arg,
                   collection,
                   one_result=False):
        db = eval("self.client."+collection)
        cursor = db.ob.find(arg)
        toret = []
        for c in cursor:
            toret.append(c)
        if one_result:
            if len(toret > 1):
                return toret[0]
        return toret

    def delete_by_arg(self,
                      arg,
                      collection):
        db = eval("self.client."+collection)
        db.ob.delete_many(arg)
