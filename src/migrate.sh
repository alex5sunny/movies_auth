#!/bin/sh

if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

echo "start migration"
#export DB_DSN="dbname=${DB_NAME} user=${DB_USERNAME} password=${DB_PASSWORD} host=${DB_HOST}"
alembic upgrade head
echo "migration complete"
