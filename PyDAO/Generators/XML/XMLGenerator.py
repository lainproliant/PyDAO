#
# XML Generator
#
# Generates Schema XML which can be later used to fuel
# a second-pass generator.
#
# (c) October 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

import os

from PyDAO.GeneratorException import *
from PyDAO.GeneratorBase import *
from PyDAO.Mapping import registerGenerator

#--------------------------------------------------------------------
class XMLGeneratorException (GeneratorException):
   pass


#--------------------------------------------------------------------
class XMLGenerator (GeneratorBase):
   """
      Generates Schema XML which can be later used to fuel
      a second-pass generator.
   """

   def __init__ (self, **kwargs):
      """
         Initializes an XMLGenerator.
      """

      GeneratorBase.__init__ (self)


   def generate (self, schema, outputPath = '.', overwrite = False):
      """
         Writes a single Schema XML file to 'outputDir', the full path
         name of the file to be written.
      """
      
      if os.path.exists (outputDir) and not overwrite:
         raise XMLGeneratorException ("File '%s' already exists and overwrite is disabled." % outputDir)

      outFile = open (outputDir, 'w')

      outFile.write (str (schema))
      outFile.close ()

#--------------------------------------------------------------------
# Register this generator in PyDAO.Mapping.
#
registerGenerator ('XML', XMLGenerator)
