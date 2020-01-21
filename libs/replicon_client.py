from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import http.client
import hashlib
import json
import os
import requests
import timeit

COMPANY_NAME = 'Avascentgroup'
USER_NAME = 'Avascent.Admin'
PASSWORD = 'CyberS3curityforAvasc3nt'
HEADER = {'content-type': 'application/json'}
CACHE_DIR = './CACHE/'

def rel_path(fn):
  return CACHE_DIR + fn

def creation_date(filename):
    t = os.path.getctime(rel_path(filename))
    return datetime.fromtimestamp(t)

class RepliconClient:
  # Create cache directory and remove all cache files older then 6 hours
  @classmethod
  def prepare(self):
    if not os.path.exists(CACHE_DIR):
      os.makedirs(CACHE_DIR)

    last_hour_date_time = datetime.now() - timedelta(hours = 1)
    for filename in os.listdir(CACHE_DIR):
      if creation_date(filename) < last_hour_date_time:
        os.remove(rel_path(filename))
  @classmethod
  def query(self, service, operation, data = {}):
    url = "https://na4.replicon.com/{}/services/{}.svc/{}".format(COMPANY_NAME, service, operation)
    cache_key = hashlib.md5((url + str(data)).encode('UTF-8')).hexdigest()
    cached_path = CACHE_DIR + '/' + cache_key

    if os.path.exists(cached_path):
      print("Query: {} (CACHE)".format(url))
      with open(cached_path) as f: content = f.read()
      return json.loads(content)

    start = timeit.default_timer()
    response = requests.post(url, data=json.dumps(data), headers=HEADER, auth=HTTPBasicAuth(COMPANY_NAME+'\\'+USER_NAME, PASSWORD))
    stop = timeit.default_timer()

    if response.status_code == 200:
        print("Query: {0} {1:.2f}s".format(url, stop - start))
        cached_file = open(cached_path, 'w' )
        cached_file.write(response.content.decode('UTF-8'))
        return json.loads(response.content)
    else:
      print("Status:{}".format(str(response.status_code)))
      print("Header: {}".format(str(response.headers)))
      print("Body: {}".format(response.content.decode('UTF-8')))
      raise "Invalid Replicon response!"
