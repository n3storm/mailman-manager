# -*- coding: utf-8 -*-
import subprocess, os

BIN = '/usr/lib/mailman/bin/'

#for caching
from hashlib import sha1
import time
import pickle

from jinja2 import Template

def cache_disk(seconds = 30, cache_folder="/tmp"):  
    def doCache(f):  
        def inner_function(*args, **kwargs):  
  
            # calculate a cache key based on the decorated method signature  
            key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest() + '.mailmanorm'  
            filepath = os.path.join(cache_folder, key)  
  
            # verify that the cached object exists and is less than $seconds old  
            if os.path.exists(filepath):  
                modified = os.path.getmtime(filepath)  
                age_seconds = time.time() - modified  
                if age_seconds < seconds:  
                    return pickle.load(open(filepath, "rb"))  
  
            # call the decorated function...  
            result = f(*args, **kwargs)  
  
            # ... and save the cached object for next time  
            pickle.dump(result, open(filepath, "wb"))  
  
            return result  
        return inner_function  
    return doCache  

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
    


class Membership(object):
    find_member_cmd = BIN + "find_member -l %s -w %s"
    members_unsubscribe_cmd = BIN + "remove_members --fromall -f %s"
    members_cmd = BIN + "list_members %s"
    members_sync_cmd = BIN + "sync_members -n -f %s %s"
    members_subscribe_cmd = BIN + "add_members -r %s %s"
    members_unsubscribe_cmd = BIN + "remove_members -f %s %s"
    members_purge_cmd = BIN + "remove_members -a %s"

    def __init__(self, lists = None, name = None):
        if lists:
            self.all = lists
        if name:
            self.name = name

    def unsubscribe(self, email):
        if isinstance(email, list) == False:
            email = [email,]
        file_name = populate('unsubscribe', email)
        raw = run(self.members_unsubscribe_cmd, file_name, self.name)

    def member_found_results(self, query):
        result_list = []
        for k, v in enumerate(query):
            v = v.replace('\n', '').lstrip().rstrip()
            if '@' in v:
                email = v.replace(' found in:','')
                result = dict(email = email, list = None, is_owner = False)
                if len(query) > k + 2:
                    if '(as owner)' in query[k + 2] or '(as owner)' in query[k + 1]:
                        result['is_owner'] = True
                result['list'] = List(query[k + 1].replace('\n', '').replace(' (as owner)', '').lstrip().rstrip())
            if result not in result_list:
                result_list.append(result)
        
        return result_list

    def find(self, member, restrict_to = None):
        if not restrict_to:
            restrict_to = self.all(as_list=True)
        results = []
        for list_f in restrict_to:
            query = run(self.find_member_cmd, list_f, member)
            #~ print query
            if len(query) > 0:
                if not 'No such list' in query[0]:
                    result = self.member_found_results(query)
                if result > 0:
                    results += result

        if len(results) == 0:
            return None
        return results

    def all(self):
        raw = run(self.members_cmd, self.name)
        cleaned = []
        for line in raw:
            line = line.replace('\n','')
            cleaned.append(line)
        return cleaned
    
    def add(self, email):
        if isinstance(email, list) == False:
            email = [email,]
        file_name = populate('subscribe', email, self.name)
        raw = run(self.members_subscribe_cmd, file_name, self.name)

    def remove(self, email):
        if isinstance(email, list) == False:
            email = [email,]
        file_name = populate('unsubscribe', email, self.name)
        raw = run(self.members_unsubscribe_cmd, file_name, self.name)

    def purge(self):
        raw = run(self.members_purge_cmd, self.name)

class List(object):
    config_cmd = BIN + "config_list -o %s %s"
    password_cmd = BIN + "change_pw -p %s -l %s"
    touch_cmd = "touch %s/conf.py"
    allowed_changes = ['moderator', 'owner', ]

    def __init__(self, name):
        self.name = name
        self.members = Membership(name = name)
        #~ self.members = self._members()
        #~ self.config = self._config()

    def configure(self, **kwargs):
        #~ print dir(self.config())
        D = dict([(varname,getattr(self.config(),varname))
                    for varname in dir(self.config())
                    if not varname.startswith("_") ]) 
        for key, value in kwargs.items():
            if key in D and key in self.allowed_changes:
                print(key,value)
                D[key] = value
        values = D        
        f = open('template/conf.py')
        t = Template(f.read())
        path = "lists/%s/%s" % (self.name.replace('.', ''), "conf.py")
        file_config = open(path, 'w')
        file_config.write(t.render(values))
        file_config.close()
        #~ "lists/%s/"

    def __unicode__(self):
        return u'%s' % self.name
    
    def __repr__(self):
        return '%s' % self.name

    def full_name(self):
        return '%s@%s' % (self.name, self.config().host_name)

    def password(self, password_string):
        if len(password_string) < 4:
            return False
        raw = run(self.password_cmd, password_string, self.name)
        return True

    def config(self):
        directory = "lists/%s/" % self.name.replace('.', '')
        path = directory + "conf.py"
        if not os.path.exists(directory):
            os.makedirs(directory)

        module = run(self.config_cmd, path, self.name)
        touch = run(self.touch_cmd, directory)
        conf_module = __import__('lists.%s.conf' % self.name.replace('.', ''), globals(), locals(), -1)
        return conf_module

class Lists(object):
    all_cmd = BIN + "list_lists -b"
    filter_cmd = BIN + "list_lists -b --virtual-host-overview=%s"

    def __getitem__(self, name):
        return self.get(name)

    def all(self, **kwargs):
        query = run(self.all_cmd)
        return self.build(query, **kwargs)
    
    def filter(self, domain):
        query = run(self.filter_cmd % domain)
        return self.build(query)
    

    def get(self, name):
        return self.all(get_list = name)
        
    def build(self, query, **kwargs):
        list_out = []
        objects_out = []
        for line in query:
            line = line.replace('\n','').lstrip().rstrip()
            object_out = List(line)
            if 'get_list' in kwargs:
                if kwargs['get_list'] == object_out.full_name():
                    return object_out
            objects_out.append(object_out)
            list_out.append(line)
        if 'as_list' in kwargs:
            return list_out
        else:
            return objects_out
    

class MailmanServer(object):

    def __init__(self):
        self.lists = Lists()
    
    def membership(self, **kwargs):
        return Membership(self.lists.all(**kwargs))

mylists = MailmanServer()

for mlist in MailmanServer().lists.all():
    print mlist.full_name()
#~ {'email': fu@fufufu, 'owner'}

#~ listas = mylists.all()
#~ for lista in mylists.all():
    #~ print "--------n---------\n"
    #~ print lista.config().real_name
    #~ print lista.config().owner
    #~ print lista.full_name()

#~ pruebas = mylists.get('pruebas@lists.getcloud.info').members()
pruebas = mylists.lists.get('pruebas@lists.getcloud.info')
tests = mylists.lists['test00@m.coolbleiben.coop']

print ">>>>>>>>>>>>>>> %s" % tests.full_name()

pruebas.configure(owner=['fuu',])
#~ print pruebas
#~ print pruebas.members()
pruebas.members.add('nestor@barriolinux.es')
#~ print pruebas.members()
#~ pruebas.password('menelao')
#~ 
#~ print listas
#~ print listas
#~ print listas[1].name
#~ print "\nMembers:\n"
#~ print listas[1].members()
#~ print "\nConfig:\n"
#~ anuncios = listas[1].config()
#~ print anuncios.real_name
#~ print listas[2].config().real_name   

print "\nFind josue:\n"
#~ found = mylists.find('josue')
found = mylists.membership().find('josue', restrict_to = ['pruebas'])
print found[0]['list'].config()

print mylists.lists.filter('getcloud.info')
for lista in  mylists.lists.filter('getcloud.info'):
    print lista.members.all()

#~ getcloud = mylists.filter('getcloud.info')
#~ print getcloud
#~ print mylists.find('nestor')[1]
