#!/bin/bash

# Initialize database
python -c "from app import init_db; init_db()"

# Start the application
exec "$@"
