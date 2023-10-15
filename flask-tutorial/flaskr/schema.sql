--delete user and post if they exist in the database
DROP TABLE IF EXISTS user;  -- drop = delete
DROP TABLE IF EXISTS post;
-- user table store the user info and it is created by three columns: id, username and password
CREATE TABLE user(
  id INTEGER PRIMARY KEY AUTOINCREMENT, --id, type: Integer every key(user) add to the table, id will be auto increment to ensure unique id for each user
  username TEXT UNIQUE NOT NULL, --username, type: string, unique make sure no dublicate for username and column can't have empty username
  password TEXT NOT NULL -- password, type: string, make sure the password user entered is not empty
);

-- post table store individual post
CREATE TABLE post(
 id INTEGER PRIMARY KEY AUTOINCREMENT, --id type integer, every user add the table, the id will increament to avoid duplicate
 author_id INTEGER NOT NULL, --author-id type integer, user who wrote the post, make sure author_id is not empty
 created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, --create the timeline of the post. timestamp is date and time value default is current date and time
 title TEXT NOT NULL, -- title of the post, make sure it's not null
 body TEXT NOT NULL,
 FOREIGN KEY(author_id) REFERENCES user (id) -- establish connection between author id and user id each one should match.
);

  
   
