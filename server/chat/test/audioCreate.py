import json

from bio_robot import utils

data_list = []

j = utils.load_json_from_file('../test/json.json')
lis = []
for i in j:
    if input(str(i['id']) + i['name']) == 'z':
        lis.append({
            'id': i['id'],
            'name': i['name']
        })
        print('加入成功')

utils.dump_to_json(lis, '../test/json.json')
