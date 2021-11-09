import sys
def run(name):
    file_name = name
    f = open(file_name)
    data = f.read()
    f.close()
    return data
