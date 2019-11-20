import concurrent.futures
import concurrent.futures
import requests
import threading
import yaml
import traceback
import psycopg2
import logging
import logging.config
import os
import sys
import time
import sqlite3
import getpass

# Global variables
threadLocal = threading.local()
hash_list = []
jobs_url = []
jobs = []
host = "http://localhost:8000/modulelog/"
choose_file = "sha.txt"
yaml_file = 'config.yaml'


def get_sites():
    """Getting job_id from sha.txt"""
    with open(choose_file, 'r') as f:
        f_content = f.readlines()
        for h in f_content:
            sha = h.split('\n')[0]
            hash_list.append(sha)
        return hash_list


def assign_url():
    """Assigning values to jobs_url []"""
    global yaml_file
    get_sites()

    with open(yaml_file, 'rt') as f:
        config = yaml.safe_load(f.read())
    thread = config['thread']
    api = thread['rest_api']

    for s in hash_list:
        site = "{}{}".format(api, s)
        jobs_url.append(site)
    return jobs_url


def get_session():
    """Starting session"""
    if not hasattr(threadLocal, "session"):
        threadLocal.session = requests.Session()
    return threadLocal.session


def download_site(url):
    """Logging data to feed"""
    session = get_session()
    with session.get(url) as response:
        data = response.json()
        logger.debug("Read {} from {}".format(data, url))
        jobs.append(data)


def download_all_sites(jobs_url):
    """Threading"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_site, jobs_url)


def setup_yaml():
    """Setup logging configuration """
    global yaml_file
    default_level = logging.DEBUG
    value = os.getenv("LOG_CFG", None)

    if value:
        yaml_file = value
    if os.path.exists(yaml_file):
        with open(yaml_file, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level, filename="error.log")
    else:
        logging.basicConfig(level=default_level, filename="debug.log")
        print('Failed to load configuration file. Using default configs')


def yaml_conf():
    with open(yaml_file, 'rt') as f:
        config = yaml.safe_load(f.read())
    thread = config['thread']
    thread_num = thread['num_of_thread']
    return thread_num


def create_db():
    try:
        sqliteConnection = sqlite3.connect('job_query.db')
        sqlite_create_table_query = '''CREATE TABLE jobs (
                                    id INTEGER PRIMARY KEY,
                                    job_id TEXT NOT NULL,
                                    app_name TEXT NOT NULL,
                                    state TEXT NOT NULL,
                                    date_created datetime);'''

        cursor = sqliteConnection.cursor()
        logger.info("Connected to SQLite database")
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()
        logger.info("SQLite table created")
        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)


def save_to_db():
    try:
        sqliteConnection = sqlite3.connect('job_query.db')
        cursor = sqliteConnection.cursor()
        logger.info("Connected to SQLite database.")

        for job in jobs:
            logger.debug("{} inserted successfully".format(job['app_name']))
            sqlite_insert_query = """INSERT INTO 'jobs'
                                      ('job_id', 'app_name', 'state', 'date_created')  VALUES  (?, ?, ?, ?)"""

            data_tuple = (job['job_id'], job['app_name'], job['state'], job['date_created'])
            cursor.execute(sqlite_insert_query, data_tuple)
            sqliteConnection.commit()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)


if __name__ == "__main__":
    setup_yaml()
    logger = logging.getLogger(__name__)
    start_time = time.time()
    assign_url()
    yaml_conf()

    if yaml_conf() is 1:
        jobs_url = jobs_url
    else:
        with open(yaml_file, 'rt') as f:
            config = yaml.safe_load(f.read())
        thread = config['thread']
        thread_num = thread['num_of_thread']
        jobs_url = jobs_url * thread_num

    download_all_sites(jobs_url)
    duration = time.time() - start_time
    logger.info("Downloaded {} data in {} seconds".format(len(jobs_url), duration))
    create_db()
    save_to_db()
