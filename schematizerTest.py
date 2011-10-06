from PyDAO.Schematizers.MySQLSchematizer import *
from getpass import getpass
import MySQLdb
import sys

def getSchema ():
   sys.stderr.write ("Username: ")
   username = raw_input ()
   tables = []

   password = getpass ("Password: ", sys.stderr)

   db = MySQLdb.connect (
         host = "localhost", 
         port = 3306, 
         user = username, 
         passwd = password)

   sys.stderr.write ("Database: ")
   databaseName = raw_input ()

   sys.stderr.write ("Tables (a,b,c/ALL) [ALL]: ")
   tableInput = raw_input ()

   if tableInput and tableInput != 'ALL':
      tables = tableInput.split (',')

   schematizer = MySQLSchematizer (dbconn = db, database = databaseName)
   return schematizer.schematize (tables)

if __name__ == "__main__":
   print str (getSchema ())

