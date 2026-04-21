-- Create chats table
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    title TEXT DEFAULT 'New Chat',
    file_context TEXT
);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    user_msg TEXT,
    ai_msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);