CREATE TABLE users (
  id INT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  passWord VARCHAR(255) NOT NULL,
index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE messages (
  id INT UNSIGNED AUTO_INCREMENT,
  postFrom VARCHAR(255) NOT NULL,
  postTo VARCHAR(255) NOT NULL,
  content VARCHAR(255) NOT NULL,
  time DATETIME DEFAULT CURRENT_TIMESTAMP,
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE group_rooms (
  id INT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  owner VARCHAR(255) NOT NULL,
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE users_groups (
  id INT UNSIGNED AUTO_INCREMENT,
  group_name VARCHAR(255) NOT NULL,
  userId VARCHAR(255) NOT NULL,
  groupId INT UNSIGNED NOT NULL,
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE groups_massages (
  id INT UNSIGNED AUTO_INCREMENT,
  groupId INT UNSIGNED NOT NULL,
  content VARCHAR(255) NOT NULL,
  sendername VARCHAR(255) NOT NULL,
  time DATETIME DEFAULT CURRENT_TIMESTAMP,
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE user_info (
  id INT UNSIGNED AUTO_INCREMENT,
  userId VARCHAR(255) NOT NULL,
  comment VARCHAR(255),
  birthday DATE,
  twitter VARCHAR(255),
  website VARCHAR(255),
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;

CREATE TABLE user_friends (
  id INT UNSIGNED AUTO_INCREMENT,
  requestId VARCHAR(255) NOT NULL,
  requestedId VARCHAR(255) NOT NULL,
  requested BOOLEAN DEFAULT false,
  approved BOOLEAN DEFAULT false,
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;
