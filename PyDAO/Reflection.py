#
# Reflection
#
# Utility functions for reflecting methods and properties
# from a Python object.
#
# (c) October 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

#--------------------------------------------------------------------
class ReflectionException (Exception): pass

#--------------------------------------------------------------------
def reflectParameter (obj, parameter, value, allowSetVariable = False):
   """
      Reflects the given parameter onto the object.

      This is done in one of the following ways, in order:

      1) If the object has a method named "set{X}", where X
         is the capitalized parameter name, this method is called
         with value as a single parameter.
      2) If the object has a property or existing attribute
         matching the parameter name, this property or attribute
         is set.
      3) Failing the above, a new attribute is set if allowSetVariable
         is specified as True.  Otherwise, a ReflectionException is thrown.

      Note that this method is only useful if you wish to reflect parameters
      by providing a 'set{X}' method instead of using a @property,
      which is the more pythonic way of doing things.
   """

   #-----------------------------------------------------------------
   # Step 1: Attempt to call 'set{Parameter}' on obj.
   
   setterName = 'set' + parameter.capitalize ()
   setter = None

   try:
      setter = getattr (obj, attrName)

   except AttributeError, excVal:
      pass

   if setter is not None:
      setter (value)
      return

   #-----------------------------------------------------------------
   # Step 2: Attempt to set 'obj.{parameter}' with existing
   #         attribute/property.

   try:
      attr = getattr (obj, parameter)
      setattr (obj, parameter, value)
      return

   except AttributeError, excVal:
      if not allowSetVariable:
         raise ReflectionException, excVal + 'or \'%s\'' % (attrName)


   #-----------------------------------------------------------------
   # Step 3: Attempt to 'setattr (obj, parameter, value)'.

   try:
      setattr (obj, parameter, value)
      return

   except Exception, excVal:
      raise ReflectionException, excVal
   
