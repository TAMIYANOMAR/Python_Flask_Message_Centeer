# message_centeer
- This is web application with python Flask and mysql.
- Please install Flask and mysql-connector
- With Mysql on Docker can easily use this application
- ログイン機能：個人パスワードとIDを用いてユーザ登録、ログインができます。
- メッセージ機能：特定の個人とメッセージのやり取りができます。過去のメッセージはSQLに残り、メッセージ一覧として確認できます。

#updates
- 2023/02/10 CSS,HTMLのアップデート フレンド機能の追加
![image](https://user-images.githubusercontent.com/59043309/218005556-8582c61a-a2e0-4a43-9344-dedeb420314c.png)
![image](https://user-images.githubusercontent.com/59043309/218005614-03933c8a-cc0c-4046-8608-7ef8726966e7.png)


# Dockerコマンドから実行可能(最新ではありません）
- シェル上で実行
```
Docker pull mysql
docker network create python-network
docker run --name mysql_con  --network python-network  -e MYSQL_ROOT_PASSWORD=mysql_pass -d -p 33306:3306 mysql
#Mysqlのhostアドレスが172.18.0.2じゃないとうまくいかないです
```
- Mysqlコンテナに入る
```
mysql -u root -p
#パスワードはmysql_pass
CREATE DAABASE kaggle;
USE kaggle;
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
```
- シェルに戻る
```
docker network inspect python-network
docker pull tamiyanomar/message-center-py:tagname
docker run --network python-network -p 5000:5000 -v ${PWD}:/app -d tamiyanomar/message-center-py:tagname
```
- http://127.0.0.1:5000/ にブラウザから接続
