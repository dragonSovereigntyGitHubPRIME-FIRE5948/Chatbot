import chromadb
import chromadb.api
from chromadb.config import Settings


##########
# CLIENT #
##########

def get_client():
    return chromadb.PersistentClient(settings=Settings(anonymized_telemetry=False))

##############
# COLLECTION #
##############

# get collections
def get_collections(client: chromadb.API):
    return client.list_collections()
# check if collection exist
def collection_exist(client: chromadb.API, name:str):
    if client.get_collection(name):
        return True
    else:
        return False
# create collection
def create_collection(client: chromadb.API, name: str):
    if collection_exist(name=name):
        print('h')
    else:
        client.create_collection(name)
# delete collection
def delete_collection(client: chromadb.API, name: str):
    if collection_exist(name=name):
        print('h')
    else:
        client.delete_collection(name=name)
# modify collection name
def modify_collection_name(new_name: str, collection: chromadb.api.Collection):
    collection.modify(new_name)

#########
# ITEMS #
#########

# get items in collection

# get number of items in collection
def count_items(collection: chromadb.api.Collection):
    return collection.count()

#
# add item
# update item
# upsert

# query
