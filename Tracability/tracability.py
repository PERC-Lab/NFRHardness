import json
from util import *

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def extract_code(cl):
    temp = cl.split(' ')
    file_name = temp[0]
    start = temp[1].split('-')[0]
    if len(temp[1].split('-')) == 1:
        end = start
    else:
        end = temp[1].split('-')[1]
    return file_name, int(start), int(end)

#locc
locc_values = []
for nfr in data:
    code_locations = nfr["code_location"]
    id = nfr["id"]
    locc = 0
    for code_location in code_locations:
        file_name,start_line,end_line = extract_code(code_location)
        locc += end_line-start_line+1
    locc_values.append(locc)
    nfr["locc"] = locc
    #print(id, locc)
print("\nLOCC Distribution:")
for locc in sorted(set(locc_values), key=lambda x: locc_values.count(x), reverse=True):
    pass
    #print(f"LOCC={locc}: {locc_values.count(locc)} requirements")

# cdc
cdc_values = []
for nfr in data:
    code_locations = nfr["code_location"]
    id = nfr["id"]
    cdc = set()
    for code_location in code_locations:
        file_name,start_line,end_line = extract_code(code_location)
        cdc.add(file_name)
    cdc = len(cdc)
    cdc_values.append(cdc)
    #print(id, cdc)
    nfr["cdc"] = cdc

print("\CDC Distribution:")
for cdc in sorted(set(cdc_values), key=lambda x: cdc_values.count(x), reverse=True):
    pass
    #print(f"CDC={cdc}: {cdc_values.count(cdc)} requirements")


# cdo
cdo_values = []
for nfr in data:
    code_locations = nfr["code_location"]
    id = nfr["id"]
    methods = set()
    for code_location in code_locations:
        file_name,start_line,end_line = extract_code(code_location)
        for m in methods_overlapping(file_name, start_line, end_line):
            methods.add(m)

    cdo = len(methods)
    cdo_values.append(cdo)
    
    #print(id, cdo)
    nfr["cdo"] = cdo

print("\CDO Distribution:")
for cdo in sorted(set(cdo_values), key=lambda x: cdo_values.count(x), reverse=True):
    pass
    #print(f"CDO={cdo}: {cdo_values.count(cdo)} requirements")

#DOCS
dosc_values = []
for nfr in data:
    code_locations = nfr["code_location"]
    id = nfr["id"]

    # 1. attribute each concern line to its containing class -> CONT per class
    lines_by_file = {}
    for code_location in code_locations:
        file_name, start_line, end_line = extract_code(code_location)
        path = find_file(file_name)
        lines_by_file.setdefault(path, set()).update(range(start_line, end_line + 1))

    
    
    cont = {}                                  # {class_id: concern_line_count}
    for path, lines in lines_by_file.items():
        classes = extract_classes(path)
        for line in lines:
            cid = innermost_class(classes, line)
            if cid is not None:                # skip imports / package lines
                cont[cid] = cont.get(cid, 0) + 1
    
    
    # 2. DOSC from the distribution (eq. 7)
    dosc_value = dosc(cont)
    dosc_values.append(dosc_value)
    print(id, dosc_value)
    nfr["docs"] = dosc_value


#DOCM
dosm_values = []
for nfr in data:
    id = nfr["id"]
    lines_by_file = {}
    for loc in nfr["code_location"]:
        file_name, start_line, end_line = extract_code(loc)
        path = find_file(file_name)
        lines_by_file.setdefault(path, set()).update(range(start_line, end_line + 1))

    cont = {}
    locc = 0
    for path, lines in lines_by_file.items():
        methods = extract_methods(path)
        classes = extract_classes(path)
        c_start, c_end, _ = classes[0]          # the single class
        for line in lines:
            if not (c_start <= line <= c_end):
                continue                        # import/package line -> excluded
            locc += 1                           # inside the class (fields included)
            mid = innermost_class(methods, line)
            if mid is not None:
                cont[mid] = cont.get(mid, 0) + 1
    dosm_values.append(dosm(cont, locc))
    #print(id, dosm(cont, locc))
    nfr["docm"] = dosm_values[-1]

with open("data-tracability.json", "w") as file:
    json.dump(data, file, indent=4)