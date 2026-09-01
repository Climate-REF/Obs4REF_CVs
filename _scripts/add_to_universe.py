import glob
import os

fp_check = []
for dir in glob.glob('./*'):
    if not os.path.isdir(dir):
        continue

    if not os.path.isfile(f'{dir}/000_context.jsonld'):
        continue

    for file in glob.glob(f'{dir}/*'):
        if '000_context' in file:
            continue
        fp_check.append(file)

facet_values = {}
for file in fp_check:
    check_file = '../WCRP-universe' + file[1:]

    second_check_file = check_file.replace('_id/','/')

    if not os.path.isfile(check_file) and not os.path.isfile(second_check_file): 
    
        if (facet := file.split('/')[1]) not in facet_values:
            facet_values[facet] = []
        facet_values[facet].append(file.split('/')[2].replace('.json',''))

for f, v in facet_values.items():
    print(f, v)