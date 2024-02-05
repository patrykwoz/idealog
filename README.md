# Idealog Backend: Springboard Capstone Project One
**Ideal**og  is an application designed to capture, track, and organize research ideas, experiments, and projects. It provides users with a platform to build relationships between various objects such as ideas, papers, experiments, and sketches. The goal is to create a comprehensive knowledge graph of interconnected ideas and resources.

## Overview
This repository provides an implementation of a REST API for deploying machine learning models to production using Celery, Redis, and Flask. The application is dockerized. Additionally, this repository contains a simplified implementation of frontend routes using Flask and Jinja templates and is deployed [here](https://idealog-83191d80bec9.herokuapp.com/). The actual frontend for Idealog is built using Node.js and React and can be found [here](https://github.com/patrykwoz/idealog-frontend).

The NLP portion of the repository building Knowledge bases is based on code in this blog: [Building a Knowledge Base from Texts: a Full Practical Example](https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa)

## Getting Started
Download Docker Desktop for Windows. Docker Compose will be automatically installed.

This solution uses Python, Flask, Celery, with Redis for messaging and Postgres for storage.

Run in this directory to build and run the app:

```
docker compose up
```

## Architecture
* A front-end web app in Flask Python which let's users add ideas to the db, create relationships between ideas, group them and finally create knowledge bases from selected ideas and knowledge sources.
* A Redis message broker
* Postgres SQL database
* Celery worker performing performance have tasks asynchronously

## Test
```
pip install pytest
pytest
```

Run with coverage report:
```
pip install coverage
coverage run -m pytest
coverage report
coverage html # open htmlcov/index.html in a browser
```

## Notes
This isn't an example of a properly architected perfectly designed distributed app. It's a simple example and a learning exercise. 

## Next Steps
* Make this backed more robust
* Deal with celery memory leaks
* Develop proper fronted in Springboard Capstone 2