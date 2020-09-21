import pymongo

class MongoDB:
  def __init__(self):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["security"]
    self.my_collection = db["policies"]

  def get_all_policies_name(self):
    return self.my_collection.find({}, {"name": 1, "_id": 0})
  
  def insert_policy(self, policy, name):
    policy = {'name': name, 'policy': policy}

    self.my_collection.insert_one(policy)

  def find_policy_by_name(self, name):
    return self.my_collection.find_one({"name": name})
  
  def update_policy_by_name(self, name, policy):
    return self.my_collection.update_one({"name": name}, {"$set": { 'policy': policy }})

db = MongoDB()