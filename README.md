# MessagingCenteer
- This is web application with python Flask and mysql.
- Please install Flask and mysql-connector
- With Mysql on Docker can easily use this application
- ログイン機能：個人パスワードとIDを用いてユーザ登録、ログインができます。
- メッセージ機能：特定の個人とメッセージのやり取りができます。過去のメッセージはSQLに残り、メッセージ一覧として確認できます。
- Dockerで動かすことができるのはかなり前のものになります。
# Updates

- 2023/02/27 webRTCを用いた1対1のビデオチャット機能を追加
- ![image](https://user-images.githubusercontent.com/59043309/231927685-260c2488-5241-4214-8f87-703f48927efa.png)
- 2023/02/21 socket通信を用いてメッセージ受信時に自動更新を行う機能を追加
- https://user-images.githubusercontent.com/59043309/220309331-b5537c49-0dc6-4006-b474-28e772fac62b.mp4


- 2023/02/19 アイコン機能を実装
- ![image](https://user-images.githubusercontent.com/59043309/219938926-767944ac-2dfa-4e75-9ce2-f2d732c2a07b.png)

- 2023/02/10 CSS,HTMLのアップデート フレンド機能を追加
- ![image](https://user-images.githubusercontent.com/59043309/218005614-03933c8a-cc0c-4046-8608-7ef8726966e7.png)


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
