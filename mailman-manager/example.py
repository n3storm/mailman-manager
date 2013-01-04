# -*- coding: utf-8 -*-
from manager import MailmanServer

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
