#
# pydao (ppdao2)
#
# MySQL DAO/VO class generator, second iteration.
#
# (c) 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

import MySQLdb
import getpass
import getopt
import sys
import os

from PyDAO.Exception import PyDAOException

#--------------------------------------------------------------------
# LRS-TODO: Further define command line parameters.
HELP_STRING = """
Usage: %s [OPTION]...

Generate DAO and/or VO class stubs for the given MySQL database tables.
"""

#--------------------------------------------------------------------
def main (argv):
   """
      Entry point for the pydao utility.
   """
   
   try:
      print "Hello, world!"

      raise PyDAOException, "Test exception."

   except PyDAOException, excVal:
      print "Caught %s" % str (excVal)

   sys.exit (0)

#--------------------------------------------------------------------
if __name__ == "__main__":
   main (sys.argv[:1])
