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
from PyDAO import SchemaMapping

HELP_STRING = """
Usage: %s [MAPPING_FILE..., OPTIONS]

Generate database access code based on the given mapping file.

MAPPING_FILE
      An XML file describing the database or databases for which
      DAO code will be generated.  For more information, see the
      PyDAO documentation.

-f    Specifies that output files should be overwritten if
      they exist.
"""

#--------------------------------------------------------------------
def main (argv):
   """
      Entry point for the pydao utility.
   """

   shortopts = "f"
   longopts = ['overwrite']

   shouldOverwrite = False
   
   opts, args = getopt.getopt (argv, shortopts, longopts)

   for opt, val in opts:
      if opt in ['-f', '--overwrite']:
         shouldOverwrite = true

   for filename in args: 
      try:
         mapping = SchemaMapping.loadFromXML (os.path.abspath (
            os.expanduser (filename)))
         mapping.runJob (overwrite = shouldOverwrite)

      except PyDAOException, excVal:
         print >>sys.stderr, "<Error processing file: %s> %s" % str (excVal)
         sys.exit (1)

   sys.exit (0)

#--------------------------------------------------------------------
if __name__ == "__main__":
   main (sys.argv[:1])
