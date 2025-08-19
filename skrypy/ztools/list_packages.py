import os
import yaml

file_config = "../config.yml"

with open(file_config) as stream:
    data_loaded = yaml.safe_load(stream)
    
print(data_loaded['packages'])

for ke, va in data_loaded['packages'].items():
    print('   '+va+', Vx.x, comment')