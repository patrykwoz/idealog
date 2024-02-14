#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER beaver;
    GRANT ALL PRIVILEGES ON DATABASE idealog TO beaver;

    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    image_url TEXT,
    password TEXT NOT NULL,
    user_type TEXT NOT NULL DEFAULT 'registered'
    );

    CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    publish_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text TEXT NOT NULL,
    url TEXT NOT NULL,
    privacy TEXT NOT NULL DEFAULT 'private',
    creation_mode TEXT NOT NULL DEFAULT 'automated',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    privacy TEXT NOT NULL DEFAULT 'private'
    );

    CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    publish_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text TEXT NOT NULL,
    url TEXT NOT NULL,
    file_url TEXT NOT NULL,
    idea_id INTEGER REFERENCES ideas(id) ON DELETE CASCADE,
    privacy TEXT NOT NULL DEFAULT 'private',
    creation_mode TEXT NOT NULL DEFAULT 'automated'
    );

    CREATE TABLE knowledge_sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    publish_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text TEXT NOT NULL,
    url TEXT NOT NULL,
    privacy TEXT NOT NULL DEFAULT 'private',
    creation_mode TEXT NOT NULL DEFAULT 'automated',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_domains (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    privacy TEXT NOT NULL DEFAULT 'private'
    );

    CREATE TABLE knowledge_bases (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    json_object JSON,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    privacy TEXT NOT NULL DEFAULT 'private',
    status TEXT NOT NULL DEFAULT 'pending',
    creation_mode TEXT NOT NULL DEFAULT 'automated',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
    );

    CREATE TABLE user_knowledge_bases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    knowledge_base_id INTEGER REFERENCES knowledge_bases(id) ON DELETE CASCADE
    );

    CREATE TABLE user_knowledge_sources (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    knowledge_source_id INTEGER REFERENCES knowledge_sources(id) ON DELETE CASCADE
    );

    CREATE TABLE idea_groups (
    id SERIAL PRIMARY KEY,
    idea_id INTEGER REFERENCES ideas(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE
    );

    CREATE TABLE connections (
    id SERIAL PRIMARY KEY,
    idea_id_1 INTEGER REFERENCES ideas(id) ON DELETE CASCADE,
    idea_id_2 INTEGER REFERENCES ideas(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_source_knowledge_domains (
    id SERIAL PRIMARY KEY,
    knowledge_source_id INTEGER REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    knowledge_domain_id INTEGER REFERENCES knowledge_domains(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_base_groups (
    id SERIAL PRIMARY KEY,
    knowledge_base_id INTEGER REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    idea_group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_base_knowledge_domains (
    id SERIAL PRIMARY KEY,
    knowledge_base_id INTEGER REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    knowledge_domain_id INTEGER REFERENCES knowledge_domains(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_base_ideas (
    id SERIAL PRIMARY KEY,
    knowledge_base_id INTEGER REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    idea_id INTEGER REFERENCES ideas(id) ON DELETE CASCADE
    );

    CREATE TABLE knowledge_base_knowledge_sources (
    id SERIAL PRIMARY KEY,
    knowledge_base_id INTEGER REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    knowledge_source_id INTEGER REFERENCES knowledge_sources(id) ON DELETE CASCADE
    );

    CREATE TABLE idea_tags (
    id SERIAL PRIMARY KEY,
    idea_id INTEGER REFERENCES ideas(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE
    );

    INSERT INTO users (email, username, image_url, password, user_type)
    VALUES
    ('admin@test.com','admin','images/default_profile_pic.jpg','mypass','admin');

    INSERT INTO ideas (name, publish_date, text, url, privacy, creation_mode, user_id)
    VALUES
    ('Test Idea', '2024-02-07' , 'My first idea!', 'https://www.google.com', 'privacy','creation_mode', 1);

EOSQL
