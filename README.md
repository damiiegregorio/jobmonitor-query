# jobmonitor-query

### Machine Problem: Concurrency

* Create an application which reads from a text file a list of Job IDs and queries a JobMonitor REST API to get all of the metadata for that job.
* It should store all the metadata retrieved into a local SQLite DB.
* The app should be configurable with the following parameters:
* URL of the REST API
* Number of threads to be used
* Your application should use logging. 
* Your application is required to use concurrency.
* You may use any concurrency library that is compatible with the requests library.


### Configuration
#### Change database name > config.yaml
```
mysql:
    host: <host>
    user: <username>
    db: <database_name>
    port: <port>
    password: <pwd>
```
#### Change REST API > config.yaml

```
thread:
  rest_api: <url>
  num_of_thread: <num>
```


### Running the program
#### Create database
```
python main.py
```


### Built With
* Python v3.7
* <b>IDE</b> - Jetbrains PyCharm Community Edition 2019 
