CREATE TABLE twitter (
  tuser varchar (255) NOT NULL PRIMARY KEY
);
 
CREATE TABLE user (
  uid int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username varchar(20) NOT NULL unique,
  oauth_token varchar(255) unique,
  oauth_secret varchar(255) unique,
--  fname varchar (255),
--  lname varchar (255),
  phone varchar(255) unique
--  twitter varchar (255) unique
--  Foreign key (uid) references twitter(tuser)
);
 

CREATE TABLE target (
  tid int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tname varchar(255) unique,
  phone varchar(255) unique,
  twitter varchar (255) unique
--  message_id int(11),
--  group_id int(11),
--  Foreign key (message_id) references message(message_id) on delete cascade,
--  Foreign key (group_id) references groups(group_id) on delete cascade
);
 

CREATE TABLE message (
  message_id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name varchar(255),
  text varchar (255),
  uid int(11),
  tid int(11),
  frequency varchar (255),
  Foreign key (uid) references user(uid) on delete cascade,
  Foreign key (tid) references target(tid) on delete cascade
);

/*
CREATE TABLE groups (
  group_id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name varchar(255),
  uid varchar(255),
  tid int(11),
  message_id int(11),
  Foreign key (uid) references user(uid) on delete cascade,
  Foreign key (tid) references target(tid) on delete cascade,
  Foreign key (message_id) references message(message_id) on delete cascade
);
*/

/*CREATE TABLE frequency (
  frequency_id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  duration int(11),
  message_id int(11),
  Foreign key (message_id) references message(message_id) on delete cascade
);
*/
