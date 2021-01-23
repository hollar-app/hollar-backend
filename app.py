from flask import Flask, request, jsonify, redirect, session, url_for, send_file
from flask_cors import CORS, cross_origin
import json
import uuid
import os
import pyrebase
import time
from datetime import datetime


from firebase_admin import credentials, firestore, initialize_app

pyrebase_config = {
  "apiKey": "AIzaSyD1HKUhaP9JGQ7rjW1SyAFsYEPnwawq1bk",
  "authDomain": "hollar-87996.firebaseapp.com",
  "databaseURL": "https://hollar-87996-default-rtdb.firebaseio.com/",
  "storageBucket": "hollar-87996.appspot.com",
  "serviceAccount": "path/to/serviceAccountCredentials.json"
}

firebase = pyrebase.initialize_app(pyrebase_config)
db = firebase.database()

PORT = "5000"
app = Flask(__name__)

# CORS
origin = "http://localhost:3000"
CORS(app, resources={r"*": {"origins": origin, "supports_credentials": True}})

# Database Structure
# - stores
#     - store ids
#         - orders
#             - pending
#                 - order ids
#             - completed
#                 - order ids
#         - store configs (storefront admin JSON upload)
#             - promotions
#             - products
#             - banner
#             - names
#         - 
        

@app.route("/store/<storeId>", methods=["GET"])
@cross_origin()
def store(storeId): 
    storeData = db.child("stores").child(storeId).get()
    return_json = {"status": "success", 'data': storeData}
    return json.dumps(return_json, default=str), 200

@app.route("/orders/<storeId>/", methods=["GET"])
@cross_origin()
def pending(storeId): 
    completed_orders = db.child("stores").child(storeId).child("orders").child("completed").order_by_child("timestamp").get()
    pending_orders = db.child("stores").child(storeId).child("orders").child("pending").order_by_child("timestamp").get()

    return_json = {"status": "success", 'completed_orders': completed_orders, 'pending_orders': pending_orders}
    return json.dumps(return_json, default=str), 200


@app.route("/orders/<storeId>/create/", methods=["POST"])
@cross_origin()
def store(storeId): 

    order_id = uuid.uuid()
    now = datetime.now()
    order_data = {
        "timestamp": time.time(),
        "formatted_time": now.strftime("%m/%d/%Y, %H:%M:%S"),
        "cost": cost,
        "description": description
    }

    pending_orders = db.child("stores").child(storeId).child("orders").child("pending").order_by_child("timestamp").get()
    pending_orders[order_id] = order_data
    pending_orders = db.child("stores").child(storeId).child("orders").child("pending").set(pending_orders)

    return_json = {"status": "success", 'pending_orders': pending_orders, "order_id": order_id}
    return json.dumps(return_json, default=str), 200


@app.route("/orders/<storeId>/complete/:orderId", methods=["GET"])
@cross_origin()
def store(storeId, orderId): 
    completed_orders = db.child("stores").child(storeId).child("orders").child("completed").order_by_child("timestamp").get()
    pending_orders = db.child("stores").child(storeId).child("orders").child("pending").order_by_child("timestamp").get()

    completed_orders[orderId] = pending_orders[orderId]
    del pending_orders[orderId]
    
    completed_orders = db.child("stores").child(storeId).child("orders").child("completed").set(completed_orders)
    pending_orders = db.child("stores").child(storeId).child("orders").child("pending").set(pending_orders)

    return_json = {"status": "success", 'completed_orders': completed_orders, 'pending_orders': pending_orders}
    return json.dumps(return_json, default=str), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

