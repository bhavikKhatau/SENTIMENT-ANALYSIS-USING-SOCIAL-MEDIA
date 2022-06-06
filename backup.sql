CREATE DATABASE IF NOT EXISTS be;
USE be;

DROP TABLE IF EXISTS `glogin`;
CREATE TABLE `glogin` (
  `Name` text NOT NULL,
  `Email id` varchar(45) NOT NULL,
  PRIMARY KEY (`Email id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `login`;
CREATE TABLE `login` (
  `name` text NOT NULL,
  `phone number` bigint(10) unsigned NOT NULL,
  `Email id` varchar(45) NOT NULL,
  `pass` varchar(45) NOT NULL,
  PRIMARY KEY (`Email id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;