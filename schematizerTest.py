from PyDAO.Schematizers import MySQLSchematizer
from getpass import getpass
import MySQLdb
import sys


def getSchematizer ():
   sys.stderr.write ("Username: ")
   username = raw_input ()

   password = getpass ("Password: ", sys.stderr)

   db = MySQLdb.connect (
         host = "localhost", 
         port = 3306, 
         user = username, 
         passwd = password)

   sys.stderr.write ("Database: ")
   databaseName = raw_input ()

   schematizer = MySQLSchematizer (db, databaseName)

   return schematizer

if __name__ == "__main__":
   print str (getSchematizer ().schematize ())

