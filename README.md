# pyfcrepo
Manage preservation referentials and agents in Fedora Commons
repositories.

## Requirements

``` bash
pip install requests pandas
```

## Fedora

Install and run Fedora.

First install java (e.g. on Ubuntu):
``` bash
sudo apt install openjdk-11-jre

```

Download Fedora:
[Fedora Commons](https://duraspace.org/fedora)


Run Fedora;
``` bash

java -Dfcrepo.namespace.registry=/home/jan/Bureau/Fedora/custom_namespaces.yml -jar fcrepo-webapp-6.0.0-jetty-console.jar
java\jdk\bin\java.exe -jar fcrepo-webapp-6.0.0-jetty-console.jar


```
Use custom namespaces




Variation on Windows

Download Java on Oracle website and run:

``` bash
C:\path\to\java\jdk\bin\java.exe -jar fcrepo-webapp-6.0.0-jetty-console.jar
C:\Applications\java\jdk\bin\java.exe -jar fcrepo-webapp-6.0.0-jetty-console.jar
```
```
## Usage

``` bash
python cli.py initrepo
python cli.py loadagents --file data/agents/EdV.csv
python cli.py loadref --unit ACV --unitDesc "Archives cantonales vaudoises" --file data/referentials/acv2.0.0.csv --version 2.0.0
python cli.py loadrecords --unit ACV --file data/records/records.csv
python cli.py moverecord --unit ACV --dosid D000002513 --refid 19132 # from acv/19135
python cli.py closerecord --unit ACV --dosid D000002513
python cli.py updateref --unit ACV --file data/referentials/acv3.0.0.csv --oldfile data/referentials/acv2.0.0.csv --version 3.0.0
python cli.py dumpref --unit ACV --file v3.html --version 3.0.0
python cli.py dumpref --unit ACV --file v2.html --version 2.0.0
python cli.py listrecords --unit ACV --refid 19135
python cli.py listrecords --unit ACV --refid 19132

## Todo

Improve listrecords
```
 