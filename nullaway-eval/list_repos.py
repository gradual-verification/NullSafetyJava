import os.path, requests, json, time

def gh_query(query, auth):
  response = requests.get(query, headers={"Authorization":"token "+auth})
  if response.status_code == requests.codes['ok']:
    return response
  elif response.status_code == 403:
    time.sleep(60)
    return gh_query(query, auth)
  else:
    print(response.json())
    exit()

def gh_query_paginated(query, auth):
  response = gh_query(query, auth)
  results = response.json()['items']
  while 'next' in response.links.keys():
    response = gh_query(response.links['next']['url'], auth)
    results.extend(response.json()['items'])
  return results

gh_token = open(os.path.expanduser("~/.ghtoken"), 'r').read().replace('\n', '')
query = 'https://api.github.com/search/code?q="com.uber.nullaway%3Anullaway%3A"+language:gradle'
results = gh_query_paginated(query, gh_token)
repos = dict()
for r in results:
  repos[r['repository']['full_name']] = r['repository']['html_url']

repos.pop("uber/NullAway", None)
print(str(len(results)) + " matches\t" + str(len(repos)) + " repos.")
for name, url in repos.items():
  print(url)
