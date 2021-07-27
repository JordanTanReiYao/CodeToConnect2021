from flask import Flask, make_response, request,jsonify,json
from flask_jsonpify import jsonpify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from pymongo import ReturnDocument
from bson import json_util
from bson.json_util import dumps
import re

client = MongoClient()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# Fields to check for in the input trade data
fieldsToHave=["regulatoryReportingDetails","date","tradeID","reportingSide",
"regulation","jurisdiction","securitiesFinancingTransactionType"]

# Query by date
@app.route('/get_by_date',methods=['GET'])
def get_by_date():
    # Get date
    dateInput=request.args.get('date',type=str)
    # Get the database
    MainDB=client['BOA']
    # Get the collection that stores the trade data
    collection=MainDB['trade_data']
    # Do In-Scope check
    dates=list(collection.find({"$and":[{"date":dateInput},{"regulation":"SFT_REPORTING"},
    {"reportingSide":"FIRM"},{ "$or": [{"jurisdiction":"UK"},{"jurisdiction":"EU"}]},
    {"$or": [{"securitiesFinancingTransactionType":"SECURITIES_LENDING"},
    {"securitiesFinancingTransactionType":"REPURCHASE"},
    {"securitiesFinancingTransactionType":"MARGIN_LENDING"},
    {"securitiesFinancingTransactionType":"BUY_BACK"}
    ]},
    { "$or": [{"regulatoryReportingDetails.reportingCounterpartyID":"FNB-UK’ "},
    {"regulatoryReportingDetails.reportingCounterpartyID":"FNB-EU"}]}
    ]}))
    # Get ID of clients that satisfy the in scope check
    ids=[i['regulatoryReportingDetails']['counterpartyID'] for i in dates]
    # Create list to hold client data that fail GTT check
    errDocsFull=[]
    clientIdUniq=set()
    for index,id in enumerate(ids):
        # Do GTT check
        results=list(client['BOA']['api_data'].find({"$and":[{id:{"$exists":True}},{"$or":
        [{"$and":[{"{}.documentId".format(id):"AML_KYC"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"LEI"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"REPORTING_CONSENT"},{"{}.status".format(id):"RED"}]}
        ]}]}))
        # If particular trade fails GTT check
        if len(results)>0:
            details=results[0]
            errDocs=list(filter(lambda x:(x['documentId']=="AML_KYC" and x["status"]=="RED") \
            or (x['documentId']=="LEI" and x["status"]=="RED") or (x['documentId']=="REPORTING_CONSENT" and x["status"]=="RED")  ,
            details[id]))
            errDocs={"client":id,"docs":errDocs}
            if id not in clientIdUniq:
                clientIdUniq.add(id)
                errDocsFull.append(errDocs)
            for item in errDocsFull:
                if item['client']==id:
                    if "trades" in item:
                        item['trades'].append(dates[index]["tradeID"])
                    else:
                        item["trades"]=[dates[index]["tradeID"]]
    
    if errDocsFull:
        return json.loads(json_util.dumps({'data':errDocsFull}))
    else:
        return jsonify(data=None)
    

# Query by trade
@app.route('/get_by_trade',methods=['GET'])
def get_by_trade():
    # Get trade id
    tradeInput=request.args.get('trade',type=str)
    # Get the database
    MainDB=client['BOA']
    # Get the collection that holds the trade data
    collection=MainDB['trade_data']
    # Do in scope check
    trades=list(collection.find({"$and":[{"tradeID":tradeInput},{"regulation":"SFT_REPORTING"},
    {"reportingSide":"FIRM"},{ "$or": [{"jurisdiction":"UK"},{"jurisdiction":"EU"}]},
    {"$or": [{"securitiesFinancingTransactionType":"SECURITIES_LENDING"},
    {"securitiesFinancingTransactionType":"REPURCHASE"},
    {"securitiesFinancingTransactionType":"MARGIN_LENDING"},
    {"securitiesFinancingTransactionType":"BUY_BACK"}
    ]},
    { "$or": [{"regulatoryReportingDetails.reportingCounterpartyID":"FNB-UK’ "},
    {"regulatoryReportingDetails.reportingCounterpartyID":"FNB-EU"}]}
    ]}))
    # Get ID of clients that satisfy the in scope check
    ids=[i['regulatoryReportingDetails']['counterpartyID'] for i in trades]
    # Create list to hold client data that fail GTT check for that particular trade
    errDocsFull=[]
    clientIdUniq=set()
    for index,id in enumerate(ids):
        # Do GTT check
        results=list(client['BOA']['api_data'].find({"$and":[{id:{"$exists":True}},{"$or":
        [{"$and":[{"{}.documentId".format(id):"AML_KYC"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"LEI"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"REPORTING_CONSENT"},{"{}.status".format(id):"RED"}]}
        ]}]}))
        # If particular trade fails GTT check
        if len(results)>0:
            details=results[0]
            errDocs=list(filter(lambda x:(x['documentId']=="AML_KYC" and x["status"]=="RED") \
            or (x['documentId']=="LEI" and x["status"]=="RED") or (x['documentId']=="REPORTING_CONSENT" and x["status"]=="RED")  ,
            details[id]))
            errDocs={"client":id,"docs":errDocs}
            if id not in clientIdUniq:
                clientIdUniq.add(id)
                errDocsFull.append(errDocs)
            for item in errDocsFull:
                if item['client']==id:
                    if "trades" in item:
                        item['trades'].append(trades[index]["tradeID"])
                    else:
                        item["trades"]=[trades[index]["tradeID"]]
    
    if errDocsFull:
        return json.loads(json_util.dumps({'data':errDocsFull}))
    else:
        return jsonify(data=None)


# Query by client
@app.route('/get_by_client',methods=['GET'])
def get_by_client():
    # Get client ID
    clientInput=request.args.get('client',type=str)
    # Get main database
    MainDB=client['BOA']
    # Get collection that holds the trade data
    collection=MainDB['trade_data']
    # Do in scope check
    trades=list(collection.find({"$and":[{"regulatoryReportingDetails.counterpartyID":clientInput},{"regulation":"SFT_REPORTING"},
    {"reportingSide":"FIRM"},{ "$or": [{"jurisdiction":"UK"},{"jurisdiction":"EU"}]},
    {"$or": [{"securitiesFinancingTransactionType":"SECURITIES_LENDING"},
    {"securitiesFinancingTransactionType":"REPURCHASE"},
    {"securitiesFinancingTransactionType":"MARGIN_LENDING"},
    {"securitiesFinancingTransactionType":"BUY_BACK"}
    ]},
    { "$or": [{"regulatoryReportingDetails.reportingCounterpartyID":"FNB-UK’ "},
    {"regulatoryReportingDetails.reportingCounterpartyID":"FNB-EU"}]}
    ]}))
    # Get ID of clients that satisfy the in scope check
    ids=[i['regulatoryReportingDetails']['counterpartyID'] for i in trades]
    # Create list to hold client data that fail GTT check for that particular trade
    errDocsFull=[]
    clientIdUniq=set()
    for index,id in enumerate(ids):
        # Do GTT check
        results=list(client['BOA']['api_data'].find({"$and":[{id:{"$exists":True}},{"$or":
        [{"$and":[{"{}.documentId".format(id):"AML_KYC"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"LEI"},{"{}.status".format(id):"RED"}]},
        {"$and":[{"{}.documentId".format(id):"REPORTING_CONSENT"},{"{}.status".format(id):"RED"}]}
        ]}]}))
        # If particular trade fails GTT check
        if len(results)>0:
            details=results[0]
            errDocs=list(filter(lambda x:(x['documentId']=="AML_KYC" and x["status"]=="RED") \
            or (x['documentId']=="LEI" and x["status"]=="RED") or (x['documentId']=="REPORTING_CONSENT" and x["status"]=="RED")  ,
            details[id]))
            errDocs={"client":id,"docs":errDocs}
            if id not in clientIdUniq:
                clientIdUniq.add(id)
                errDocsFull.append(errDocs)
            for item in errDocsFull:
                if item['client']==id:
                    if "trades" in item:
                        item['trades'].append(trades[index]["tradeID"])
                    else:
                        item["trades"]=[trades[index]["tradeID"]]
           
    if errDocsFull:
        return json.loads(json_util.dumps({'data':errDocsFull}))
    else:
        return jsonify(data=None)


# Upload files
@app.route('/upload_files',methods=['POST'])
def upload_files():
       
    MainDB=client['BOA']
    
    collection=MainDB['trade_data']
    
    # Get files to be uploaded 
    uploaded_files = request.files.getlist("files[]")
    for f in uploaded_files:
        finalised=[json.loads(re.match('^(.*?)(\r{0,1})(\n{0,1})$',line.decode()).group(1)) for line in f]
        for data in finalised:
            # Check that input trade data have all the required fields
            for field in fieldsToHave:
                if field not in data.keys():
                    return jsonify({'message':'Some trades are missing {} field'.format(field)}) 
        collection.insert_many(finalised)
    
    return jsonify({'message':'File uploaded successfully!'}) 
      

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000,debug=True)