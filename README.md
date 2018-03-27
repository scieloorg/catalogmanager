# Catalog Manager

## Requirements:

- CouchDB
- Pyramid

## Test Environment:

### CouchDB

```
docker pull couchdb
docker run -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password -td --name my-couchdb couchdb

```
