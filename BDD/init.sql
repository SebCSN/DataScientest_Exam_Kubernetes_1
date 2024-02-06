CREATE DATABASE IF NOT EXISTS `bdd_test`;

USE bdd_test;

CREATE TABLE IF NOT EXISTS Users (
  id INT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL
);

INSERT INTO Users(id, username, email) VALUES (1, 'Seb-C', 'seb@seb.c');
INSERT INTO Users(id, username, email) VALUES (2, 'Mu-R', 'mu@mu.c');
