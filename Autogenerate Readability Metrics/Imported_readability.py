import readabilitypack as rea
import sys
file_name = sys.argv[1]
f = open(file_name)
data = f.read()
f.close()
results = rea.getmeasures(data, lang='en')
print(results)