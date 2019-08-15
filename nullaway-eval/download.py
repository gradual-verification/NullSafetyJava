from common import *

for url in repos:
    get_repo(url)
    apply_patch(url)
