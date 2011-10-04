#
# ClassLoader
#
# A module providing methods to dynamically load python
# modules and classes using fully qualified names.
#
# Inspired by StackOverflow:
# http://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
#
# Thanks to Jason Baker.
#
# (c) 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

import inspect

#--------------------------------------------------------------------
class ClassLoaderException (Exception): pass

#--------------------------------------------------------------------
class ClassLoader (object):
   """
      A class which assists in loading classes, modules,
      and other related data.
   """

   def __init__ (self):
      """
         Initializes a ClassLoader.
      """
      
      pass


   def loadModule (self, moduleName):
      """
         Loads and returns the given module.
      """

      module = __import__ (moduleName)
      path = moduleName.split ('.')
      for component in path [1:]:
         try:
            module = getattr (module, component)
         
         except AttributeError, excVal:
            raise ClassLoaderException, excVal

      return module

   
   def loadFromModule (self, objectName):
      """
         Loads an arbitrary object from the given module
      """

      path = objectName.split ('.')

      if len (path) < 2:
         raise ClassLoaderException, "Invalid object path: %s" % objectName

      modulePath = '.'.join (path [:-1])
      objectBaseName = path [-1]

      module = self.loadModule (modulePath)

      try:
         obj = getattr (module, objectBaseName)

      except AttributeError, excVal:
         raise ClassLoaderException, excVal

      return obj


   def loadClass (self, className):
      """
         Loads and returns the given object.
         This method will throw a ClassLoaderException if the object
         is not a class.
      """

      obj = self.loadFromModule (className)

      if not inspect.isclass (obj):
         raise ClassLoaderException, 'Object "%s" is not a class.' % obj

      return obj

