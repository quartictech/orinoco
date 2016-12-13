import shapefile

names = []
sf = shapefile.Reader("shapes/Gas_Site")

for record in sf.records():
    names.append(record[2].lower())

sf = shapefile.Reader("shapes/OHL")

for record in sf.records():
    print(record)
    names.append(record[4].lower())

print(names)
