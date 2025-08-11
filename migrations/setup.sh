#!/bin/bash
set -e

CASSANDRA_HOST="scylla"
CASSANDRA_PORT=9042
USERNAME="cassandra"
PASSWORD="cassandra"

cassandra_ready() {
    # cqlsh -u "$USERNAME" -p "$PASSWORD" "$CASSANDRA_HOST" "$CASSANDRA_PORT" -e "DESCRIBE KEYSPACES" > /dev/null 2>&1
    cqlsh "$CASSANDRA_HOST" "$CASSANDRA_PORT" -e "DESCRIBE KEYSPACES" > /dev/null 2>&1
}

echo "Waiting for Scylla to be ready..."
until cassandra_ready; do
  sleep 5
  echo "Retrying..."
done

echo "Scylla is ready. Running migrations..."
# cqlsh -u "$USERNAME" -p "$PASSWORD" "$CASSANDRA_HOST" "$CASSANDRA_PORT" -f /usr/setup.cql
cqlsh "$CASSANDRA_HOST" "$CASSANDRA_PORT" -f /usr/setup.cql


echo "Migration completed."
