Database organization
=====================

Database name
-------------
* mxdata
```
> use mxdata
switched to db mxdata
```

Main collections
----------------
* **Datasets** - stores Scan Request messages sent by DA+Server
* **Adp** - stores messages sent by Automatic Data Processing (adp) service. This collection is used by Adp Tracker
* **Merge** - stores results of merging jobs run by ```adp```. This collection is also user by Adp Tracker 

Auxiliary collections
---------------------
* **Stream** - capped collection. Flask application is running a ```tail cursor``` query on it to generate SSE events for Adp Tracker.
Each document that is inserted to **Datasets**, **Adp** or **Merge** collection is also inserted to **Stream** collection
* **Abort** - capped collection, used by ```adp``` to abort data processing jobs
* **MergeState** and **CurrentMergeId** - collections to store current state of merging jobs launched by ``adp``. 
Used by ```MergeManager.py``` and ```MergeWorker.py``` deamons.
* **Spreadsheet** - collection to keep sample spreadsheet.
* **PuckInventory** - collection to keep sample pucks.
* **Shipping** - collection to keep shipping dewars. 


Collection indexes 
------------------

* Abort

   ```
   db.createCollection( "Abort", { capped: true, size: 500000 } ) // 500kB
   ```

* Stream

   ```
   db.createCollection( "Stream", { capped: true, size: 100000 } ) // 100kB
   ```

* Datasets

   ```
   db.Datasets.createIndex({beamline:1, createdOn:1})
   db.Datasets.createIndex({userAccount:1, beamline:1})
   ```

* Adp

   ```
   db.Adp.createIndex({userAccount:1, beamline:1, createdOn:1, method:1, seen:1})
   db.Adp.createIndex({ 'metadata.name': 1, 'metadata.value':1 })
   ```

* Merge

   ```
   db.Merge.createIndex({userAccount:1, beamline:1, createdOn:1, method:1, seen:1, mergeId:1})
   db.Merge.createIndex({ 'metadata.name': 1, 'metadata.value':1 })
   ```

* MergeState

   ```
   db.MergState.createIndex({userAccount: 1, beamline: 1, trackingId: 1})
   db.MergState.createIndex({userAccount: 1, beamline: 1, mergeId: 1})
   ```

* CurrentMergeId

   ```
   db.CurrentMergeId.createIndex({userAccount:1, beamline:1})
   ```

* PuckInventory ``not in production``

   ```
   db.PuckInventory.createIndex({userAccount:1})
   ```

* Shipping ``not in production``

   ```
   db.Shipping.createIndex({userAccount:1})
   ```

MXDB server REST API
====================

API to access, insert and update documents in mxdb in implemented as Python Flask application.
Access to all endpoints is implemented in ```mxdbclient``` package

*  ```src/app/``` - location of API endpoints

* ```db/query``` - GET, implemented in ```src/app/queryView.py```
    * query items can be passed as arguments, ```db/query?userAccount=e15880&beamline=x06sa?collection=Datasets```
    * query items can be in request body as json ```{userAccount:e15880, beamline:x06sa, collection=Datasets}```
    
* ```db/insert``` PUT, implemented in ```src/app/insertView.py```
    * document to insert specified in request body request body as json ```{userAccount:e15880, beamline:x06sa}```

* see  ```src/app/``` for all other exposed API points customied to selected services, for instance AdpTracker or Adp
  
Queries
-------
Each query is constructed by constructing JSON with ```key:value``` pairs against the documents stored in the database.
JSON query is PUT to ```/db/query``` endpoint as message body.

The schemas of documents in stored in each of database collection are found in ```examples``` directory.

* find all ScanRequest for user e15880 at X06SA beamline

```python
{"collection" : "Datasets",
 "userAccount": "e15880",
 "beamline": "X06SA"}
``` 

* find all processed datasets for user e10003, X10SA beamline, only standard data collection 

```python
{"collection" : "Adp",
 "userAccount": "e10003",
 "beamline": "X10SA",
 "method": "standard"}
```

Special API arguments
---------------------
When querying database, special arguments can be used to modify query result:

* ```collection``` - each query to database needs specify collection which is queried, **required** 
    * one of ```['Datasets', 'Adp', 'Merge', 'Abort', 'Stream', 'MergeState', 'CurrentMergeId', 'Spreadsheet']```

```python
{"collection" : "Datasets",
 "userAccount": "e15880",
 "method": "standard"}

```    
 
* ```after``` and ```before``` - query date range, optional

```python
{"collection" : "Datasets",
 "userAccount": "e15880",
 "method": "standard",
 "after": "2019-10-10"}

```

* ```qtype``` - mongo query type, optional
    * one of ```['find', 'distinct', 'find_one', 'aggregate']```. Default is ```find```

```python
{"collection" : "Datasets",
 "userAccount": "e15880",
 "method": "standard",
 "after": "2019-10-10",
 "qtype": "find_one"}
```

* access to all API endpoints is implemented in ```mxdbclient``` package
