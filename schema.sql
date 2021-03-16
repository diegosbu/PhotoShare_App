CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

SELECT imgdata, photo_id, caption FROM Photos WHERE photo_id IN 
					(SELECT P.photo_id FROM Tagged T, Photos P WHERE T.tag_name = "what" AND P.user_id = 1 AND P.photo_id = T.photo_id);

SELECT * FROM Tagged;
SELECT album_id FROM Albums WHERE owner_id = 2 AND album_name = 'DEFAULT' LIMIT 1;

CREATE TABLE IF NOT EXISTS Users(	
  user_id INTEGER AUTO_INCREMENT,
	fname  VARCHAR(100) NOT NULL DEFAULT '',
	lname VARCHAR(100) NOT NULL DEFAULT '',
	email VARCHAR(255),
	hometown VARCHAR(100),
	dob DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL 1 YEAR),
	gender VARCHAR(100),
	password VARCHAR(100) NOT NULL DEFAULT '',
	UNIQUE (email),
  CONSTRAINT users_pk PRIMARY KEY (user_id));

CREATE TABLE IF NOT EXISTS Photos(	
  photo_id INTEGER AUTO_INCREMENT,
	imgdata LONGBLOB NOT NULL,
	user_id INTEGER NOT NULL,
	caption VARCHAR(30), 
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT photos_pk PRIMARY KEY (photo_id)
);

CREATE TABLE IF NOT EXISTS Albums(	
  album_id INTEGER AUTO_INCREMENT,
  album_name VARCHAR(30) NOT NULL,
	owner_id INTEGER NOT NULL,
	date_created DATE NOT NULL, 
	FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE IF NOT EXISTS Comments(  
  comment_id INTEGER AUTO_INCREMENT,
	comment_text VARCHAR(280) NOT NULL,
	owner_id INTEGER NOT NULL,
	date_created DATE NOT NULL,
  photo_id INTEGER NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);

CREATE TABLE IF NOT EXISTS Tags( 
  tag_name VARCHAR(30) NOT NULL,
  CONSTRAINT tags_pk PRIMARY KEY (tag_name) 
);

CREATE TABLE IF NOT EXISTS Likes( 
  user_id INTEGER,
	photo_id INTEGER,
  CONSTRAINT likes_pk PRIMARY KEY (user_id, photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Friends( 
  user_id INTEGER,
	friend_id INTEGER,
  CONSTRAINT friends_pk PRIMARY KEY (user_id, friend_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (friend_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PhotoAlbums( 
  album_id INTEGER NOT NULL,
	photo_id INTEGER,
  CONSTRAINT photo_album_pk PRIMARY KEY (photo_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tagged( 
  tag_name VARCHAR(30),
  photo_id INTEGER,
  CONSTRAINT tagged_pk PRIMARY KEY (tag_name, photo_id),
  FOREIGN KEY (tag_name) REFERENCES Tags(tag_name) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE
);