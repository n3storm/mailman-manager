# -*- coding: utf-8 -*-
import subprocess
from caching import cache_disk

@cache_disk(seconds = 60, cache_folder="/tmp")
def run(cmd, *args):
    cmd = cmd % args
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = []
    for line in p.stdout:
        output.append(line)
        #~ if "find_members" in cmd:
            #~ print output
    return output

def populate(action, items, list_name = None):
    file_path = "lists/%s.txt" % action
    if list_name:
        file_path = "lists/%s/%s.txt" % (list_name, action)
    f = open('%s' % file_path, 'w')
    for item in items:
        f.write("%s\n" % item)
    f.close()
    return file_path
