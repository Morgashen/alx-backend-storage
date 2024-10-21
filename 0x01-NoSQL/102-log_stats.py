#!/usr/bin/env python3
"""
Provides statistics about Nginx logs stored in MongoDB.
"""

from pymongo import MongoClient
import sys

def print_nginx_stats(mongo_collection):
    """
    Prints statistics about the Nginx logs stored in a MongoDB collection.

    Args:
        mongo_collection (pymongo.collection.Collection): The MongoDB collection object.
    """
    log_count = mongo_collection.count_documents({})
    print(f"{log_count} logs")

    print("Methods:")
    methods = mongo_collection.aggregate([
        {"$group": {"_id": "$method", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    for method in methods:
        print(f"    method {method['_id']}: {method['count']}")

    print("Status check")
    status_200 = mongo_collection.count_documents({"status": "200"})
    print(f"{status_200} status check")

    print("IPs:")
    top_ips = mongo_collection.aggregate([
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    for ip_doc in top_ips:
        print(f"    {ip_doc['_id']}: {ip_doc['count']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 12-log_stats.py <database_name>")
        sys.exit(1)

    database_name = sys.argv[1]
    client = MongoClient()
    db = client[database_name]
    nginx_collection = db.nginx

    print_nginx_stats(nginx_collection)
