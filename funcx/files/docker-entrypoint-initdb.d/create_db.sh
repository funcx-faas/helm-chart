#!/usr/bin/env bash
PGPASSWORD=leftfoot1 psql -U funcx -d public < docker-entrypoint-initdb.d/funcx-schema.sql