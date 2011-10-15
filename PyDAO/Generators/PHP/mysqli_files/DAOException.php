<?php
class DAOException extends Exception {
   function __construct ($message, $error = "", $affected_rows = 0) {
      parent::__construct ($message);
      $this->error = $error;
      $this->affected_rows = $affected_rows;
   }
}
?>
