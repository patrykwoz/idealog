INSERT INTO users (email, username, image_url, password, user_type)
VALUES
  ('admin@test.com','admin','images/default_profile_pic.jpg','$2b$12$MFghdZrszfa08tlkPx07xO65bjW4AmL7hRxn5uZJ.pK5YSBmqrUSG','admin');

INSERT INTO ideas (name, publish_date, text, url, privacy, creation_mode, user_id)
VALUES
  ('Test Idea', '2024-02-07' , 'My first idea!', 'https://www.google.com', 'privacy','creation_mode', 1);