import os

user_input = "/home/olivier/Documents/eclipse-workspace/skrypy/NodeEditor/python"
directory = os.listdir(user_input)

searchstring = "/tmp"

for fname in directory:
    # print(fname)
    if os.path.isfile(user_input + os.sep + fname):
        # Full path
        f = open(user_input + os.sep + fname, 'r')

        if searchstring in f.read():
            print('found string in file %s' % fname)
        else:
            print('string not found')
        f.close()