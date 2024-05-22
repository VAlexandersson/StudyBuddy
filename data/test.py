import json

with open('ds4 copy.json', 'r') as f:
  data = json.load(f)

for item in data:
  if item['Chunk'][0] == '|':
    item['Type'] = 'table'
  elif item['Chunk'][0] == '**Fig':
    item['Type'] = 'figure'
  elif item['Chunk'][0] == '_':
    item['Type'] = 'math'
  elif not item['Chunk'].endswith('.'):
    item['Type'] = 'noend'
  elif item['Chunk'][0].islower():
    item['Type'] = 'nostart'


with open('ds4.json', 'w') as f:
  json.dump(data, f, indent=2)