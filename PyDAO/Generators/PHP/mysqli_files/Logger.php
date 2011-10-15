<?php

/*
 * Logger: A class to manage log file creation and usage.
 * (c) 2011 Lee Supe (lain_proliant)
 * Released under the GNU General Public License.
 */

class LoggerException extends Exception {
   function __construct ($message) {
      parent::__construct ($message);
   }
}

class Logger {
   const LEVEL_DEBUG = 200;
   const LEVEL_DIAG = 100;
   const LEVEL_INFO = 0;
   const LEVEL_CRITICAL = -100;
   const LEVEL_EMERGENCY = -200;

   private $logLevel;
   private $logFileName;
   private $logSource = "";

   function __construct ($logFileName, $level = Logger::LEVEL_INFO)
   {
      $this->logLevel = $level;
      $this->logFileName = $logFileName;

      if (! file_exists ($this->logFileName)) {
         $this->logInfo ("Log file created.");
      }
   }

   public function log ($message, $level = Logger::LEVEL_INFO)
   {
      if ($level >= $this->logLevel) {
         $logFile = fopen ($this->logFileName, "a");
         
         if ($logFile == FALSE) {
            throw new LoggerException ("Could not open the log file for writing!");
         }
         
         fwrite ($logFile, $message);

         fclose ($logFile);
      }
   }
   
   public function logDebug ($message, $level = Logger::LEVEL_DEBUG)
   {
      $this->log (sprintf ("(DBG) [%s] <%s> %s\n",
         date ("c"), $this->getLogSource (), $message, $level));
   }

   public function logInfo ($message, $level = Logger::LEVEL_INFO)
   {
      $this->log (sprintf ("(IFO) [%s] <%s> %s\n",
         date ("c"), $this->getLogSource (), $message, $level));
   }

   public function logError ($message, $level = Logger::LEVEL_CRITICAL)
   {
      $this->log (sprintf ("(ERR) [%s] <%s> %s\n",
         date ("c"), $this->getLogSource (), $message, $level));
   }

   public function logFatal ($message, $level = Logger::LEVEL_CRITICAL)
   {
      $this->log (sprintf ("(DIE) [%s] <%s> %s\n",
         date ("c"), $this->getLogSource (), $message, $level));
   }

   /**
    * Sets a string that gets displayed after the log type.
    * This message indicates the source or context of the
    * information or condition which is being logged.
    */ 
   public function setLogSource ($logSource)
   {
      $this->logSource = $logSource;
   }
   
   /**
    * Gets the currently set source or context for logging.
    * If no source is set, the QUERY_STRING is returned if possible.
    * Otherwise, an empty string is returned. 
    */
   public function getLogSource ()
   {
      if (empty ($this->logSource)) {
         if (empty ($_SERVER ['QUERY_STRING'])) {
            return "";
         } else {
            return $_SERVER ['QUERY_STRING'];
         }

      } else {
         return $this->logSource ();
      }
   }
   
   /**
    * Sets the log level.  Only messages with a level
    * lower than or equal to this value are written
    * to the log file.
    */
   public function setLogLevel ($level)
   {
      $this->logLevel = $level;
   }
}

?>
