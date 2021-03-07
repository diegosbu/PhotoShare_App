CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
-- DROP TABLE IF EXISTS Pictures CASCADE;
-- DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users 
(	
  user_id INTEGER AUTO_INCREMENT,
	fname  VARCHAR(100) NOT NULL,
	lname VARCHAR(100) NOT NULL,
	email VARCHAR(255) NOT NULL,
	hometown VARCHAR(100),
	dob DATE NOT NULL,
	gender VARCHAR(100),
	password VARCHAR(100) NOT NULL,
	UNIQUE (email),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE Photos 
(	
  photo_id INTEGER AUTO_INCREMENT,
  user_id INTEGER,
	data VARBINARY(8) NOT NULL,
	caption VARCHAR(30), 
  CONSTRAINT photos_pk PRIMARY KEY (photo_id)
);

CREATE TABLE Albums 
(	
  album_id INTEGER AUTO_INCREMENT,
  album_name VARCHAR(30) NOT NULL,
	owner_id INTEGER NOT NULL,
	date_created DATE NOT NULL, 
	FOREIGN KEY (owner_id) REFERENCES Users(user_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE Comments 
(  
  comment_id INTEGER AUTO_INCREMENT,
	comment_text VARCHAR(280) NOT NULL,
	owner_id INTEGER NOT NULL,
	date_created DATE NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES Users(user_id) 
  ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);

CREATE TABLE Tags 
( 
  tag_id INTEGER,
  tag_name VARCHAR(30) NOT NULL,
  CONSTRAINT tags_pk PRIMARY KEY (tag_id) 
);


--Relationship between photos and users
CREATE TABLE Likes 
( 
  user_id INTEGER,
	photo_id INTEGER,
  CONSTRAINT likes_pk PRIMARY KEY (user_id, photo_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE
);

--Relationship between users following other users
CREATE TABLE Follows 
( 
  user_id INTEGER,
	friend_id INTEGER,
  CONSTRAINT follows_pk PRIMARY KEY (user_id, friend_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON   UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (friend_id) REFERENCES Users(user_id) ON
  UPDATE CASCADE ON DELETE CASCADE
);

-- Relationship between albums and photos:
CREATE TABLE Inside 
( 
  album_id INTEGER,
	photo_id INTEGER,
  CONSTRAINT photo_album_pk PRIMARY KEY (photo_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id), ON UPDATE CASCADE ON DELETE CASCADE
);

-- Relationship between tags and photos
CREATE TABLE Contain ( 
  tag_name VARCHAR(30),
	photo_id INTEGER,
  CONSTRAINT tag_photo_pk PRIMARY KEY (tag_name, photo_id),
  FOREIGN KEY (tag_name) REFERENCES Tags(tag_name) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE
);


-- Relationship between comments and photos
CREATE TABLE Have 
( 
  comment_id INTEGER NOT NULL,
	photo_id  INTEGER NOT NULL,
  CONSTRAINT photo_comment_pk PRIMARY KEY (comment_id),
  FOREIGN KEY (comment_id) REFERENCES Comments(comment_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON UPDATE CASCADE ON DELETE CASCADE 
);

