
import psycopg2
from psycopg2 import extensions
import sys

try:
   #Define our connection string
   ## conn_string = "host='localhost' dbname='datadev' user='ashnet' password='Uno12mazurca'"
 
    # print the connection string we will use to connect
   # print "Connecting to database\n	->%s" % (conn_string)
 
    # get a connection, if a connect cannot be made an exception will be raised here
    ##conn = psycopg2.connect(conn_string)
    print "Connected!\n"
except:
    print "I am unable to connect the database!"
