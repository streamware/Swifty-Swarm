-- Create the 'messages' keyspace
CREATE KEYSPACE IF NOT EXISTS messages WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Use the 'messages' keyspace
USE messages;

-- Create a table 'conversations'
CREATE TABLE IF NOT EXISTS messages.conversations (
    conversation_id uuid,
    belongs_to uuid,
    conversation_type text,
    avatar text,
    opposite_party_id uuid,
    opposite_party_name text,
    last_message_id uuid,
    last_message_content text,
    last_message_timestamp timestamp,
    last_seen_message_id uuid,
    last_seen_message_timestamp timestamp,
    PRIMARY KEY ((conversation_id, belongs_to))
) WITH compression = {'sstable_compression': 'LZ4Compressor'};

-- Create an index on 'conversations'
CREATE INDEX ON messages.conversations (belongs_to);

-- Create a table 'private_messages'
CREATE TABLE IF NOT EXISTS messages.private_messages (
    conversation_id uuid,
    id uuid,
    sender_id uuid,
    recipient_id uuid,
    content text,
    created_at timestamp,
    updated_at timestamp,
    PRIMARY KEY ((conversation_id, recipient_id), created_at, id)
) WITH CLUSTERING ORDER BY (created_at DESC, id ASC)
AND compression = {'sstable_compression': 'LZ4Compressor'};
