import json

with open("../data/supporters.json", "r") as f:
    s = json.load(f)

data = s['patrons']
print(len(data))
sdata = set(data)
ndata = sorted(list(sdata))
print(len(ndata))

for i, n in enumerate(ndata):
    ndata[i] = ndata[i].strip()

ndata = {'patrons': ndata}

with open("../data/supporters.json", "w") as f:
    json.dump(ndata, f, indent=2)