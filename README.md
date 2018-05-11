# Catalog Manager

Catalog Manager is a database of XMLs and digital assets that is part of the
suite of programs that make up the SciELO Publishing Framework.

Its main characteristics are:

     * Support for multiple versions of the articles;
     * Durability of data;
     * Independence from the central node of the SciELO Network;
     * Ensuring the referential integrity between the XML article and its
       digital assets;
     * Continuous synchronization with a remote node;
     * Access to data through RESTful interfaces.


## Requirements:

- CouchDB
- Pyramid


## Test Environment:

### CouchDB

By now you need to have a running instance of CouchDB in order to run tests or
even a local development instance. Feel free to install and use it the way you
like. If you are familiar to Docker you may start one as the example below:

```bash
docker pull couchdb
docker run -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password -td --name my-couchdb couchdb
```


## Use license

Copyright 2018 SciELO <scielo-dev@googlegroups.com>. Licensed under the terms
of the BSD license. Please see LICENSE in the source code for more
information.

https://github.com/scieloorg/catalogmanager/blob/master/LICENSE

