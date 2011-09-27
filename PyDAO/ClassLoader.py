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

      module = __import__ (name)
      path = name.split ('.')
      for component in path [1:]:
         try:
            module = getattr (module, component)
         
         except AttributeError, excVal:
            raise ClassLoaderException, excVal

      return module


   def loadClass (self, className):
      """
         Loads and returns the given class
         within the given module.
      """

      path = name.split ('.')

      if len (path) < 2:
         raise ClassLoaderException, "Invalid module/class path: %s" % className

      modulePath = path [:-1]
      className = path [-1]

      module = self.loadModule (modulePath)

      try:
         classObj = getattr (module, className)

      except AttributeError, excVal:
         raise ClassLoaderException, excVal

      return classObj

