import json
import math

with open('./output.json', 'r', encoding='utf-8') as f:
  output = json.load(f)

pairdict: dict[str, float] = {}
for company, content in output['layers'].items():
  pairdict[company] = content['length_m']
pairs = sorted(pairdict.items(), key=lambda item: item[1], reverse=True)

pairdict_line: dict[str, float] = {}
for company, content in output['layers'].items():
  for path in content['paths']:
    pairdict_line[company + path['label']] = path['length_m']
pairs_line = sorted(pairdict_line.items(), key=lambda item: item[1], reverse=True)

with open('./pre.txt', 'w', encoding='utf-8') as f:
  f.write('## 会社別総延長ランキング\n\n')
  for i in range(len(pairs)):
    f.write(f'- {i+1}位 {pairs[i][0]}: {math.floor(int(pairs[i][1])/10)/100}km\n')
  f.write('\n## 路線別総延長ランキング\n\n')
  for i in range(len(pairs_line)):
    f.write(f'- {i+1}位 {pairs_line[i][0]}: {math.floor(int(pairs_line[i][1])/10)/100}km\n')
