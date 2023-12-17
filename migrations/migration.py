from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')

cluster = Cluster(['127.0.0.1'], port=9042, auth_provider=auth_provider)
session = cluster.connect('messages')

session.execute(
    """
		CREATE TABLE IF NOT EXISTS conversations (
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
		)
		WITH compression = {'sstable_compression': 'LZ4Compressor'};
    """
)

session.execute(
	"""
		CREATE INDEX ON conversations (belongs_to);
	"""
)

session.execute(
	"""
	CREATE TABLE IF NOT EXISTS private_messages (
	    conversation_id uuid,
		id uuid,
		sender_id uuid,
		recipient_id uuid,
		content text,
		created_at timestamp,
		updated_at timestamp,
		PRIMARY KEY ((conversation_id, recipient_id), created_at, id)
	)
	WITH CLUSTERING ORDER BY (created_at DESC, id ASC)
	AND compression = {'sstable_compression': 'LZ4Compressor'};
	"""
)