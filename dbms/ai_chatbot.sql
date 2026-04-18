CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INT,
    user_msg TEXT,
    ai_msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);