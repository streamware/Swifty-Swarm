#!/bin/bash

# Variables for credentials and host
CASSANDRA_HOST='127.0.0.1'
CASSANDRA_PORT=9042
USERNAME='cassandra'
PASSWORD='cassandra'

# Function to check if Cassandra is ready
cassandra_ready() {
    cqlsh -e "describe keyspaces" "$CASSANDRA_HOST" "$CASSANDRA_PORT" -u "$USERNAME" -p "$PASSWORD" > /dev/null 2>&1
}

# Wait for Cassandra to be ready
echo "Waiting for Cassandra to be ready..."
until cassandra_ready; do
  sleep 5
  echo "Retrying..."
done

echo "Cassandra is ready. Executing setup script."

# Run the CQL script
cqlsh -u "$USERNAME" -p "$PASSWORD" -f /usr/setup.cql "$CASSANDRA_HOST" "$CASSANDRA_PORT"
