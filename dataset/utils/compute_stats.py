import os

import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['linter-extraction']

stats_file = open('stats.csv', 'w')
stats_file.write('rule,violations_count,fixes_count,unique_fixes_count,files_count\n')

rule_ids = db.list_collection_names()
rule_ids.sort()
for rule_id in rule_ids:
    violations_count = db[rule_id].count_documents({})
    fixes_count = db[rule_id].count_documents({'fix': {'$exists': True}})
    files_count = len(db[rule_id].distinct('filePath'))

    fixes_df = pd.DataFrame(list(db[rule_id].find({'fix': {'$exists': True}}, {'filePath': 1, 'line': 1})))
    unique_fixes_count = len(fixes_df.drop_duplicates(subset=['filePath', 'line'], keep=False))

    stats_file.write(f'{rule_id},{violations_count},{fixes_count},{unique_fixes_count},{files_count}\n')

stats_file.close()

client.close()
