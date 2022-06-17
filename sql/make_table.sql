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
  index(id)
)ENGINE=InnoDB DEFAULT charset=utf8;
