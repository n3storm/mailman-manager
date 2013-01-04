# -*- coding: utf-8 -*-
from manager import MailmanServer

mylists = MailmanServer()

#MailmanServer has
# lists: a Lists object with all List object
# membership: for global members methods, like find
#MailmanServer > Lists has:
# 

for mlist in MailmanServer().lists.all():
    print mlist.full_name()
    # full_name is the form name@hostname

#You can use get to select one list:
testlist = mylists.lists.get('testlist@lists.example.com')

#Or select it like a dictionary:
otherlist = mylists.lists['otherlist@lists.example.com']

#Retrieving full config of a list is expensive, do not abuse or catch it in your application:
print mylists.lists['spamlist@lists.example.com'].config()

#Configure a list using kwargs:
testlist.configure(owner=['fuu@example.com',])

#Here there are subscribed and owners emails:
testlist.members()

#Add a member is as simple as this:
testlist.members.add('nestor@coolbleiben.coop')

print testlist.members()

#Change list password for admin:
testlist.password('ourpassword')
#Another way:
mylists.lists['spamlist@lists.example.com'].password('anotherpassword')

#Find if an email is subscribed in some or all the lists:
found = mylists.membership().find('john', restrict_to = ['testlist',])

#Find all lists with hostname lists.otherexample.com:
print mylists.lists.filter('lists.otherexample.com')
for nlist in mylists.lists.filter('lists.otherexample.com'):
    print nlist
