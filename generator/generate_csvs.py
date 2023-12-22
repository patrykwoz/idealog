"""Generate CSVs of random data for  development and testing of Idealog.
"""

import csv
from random import choice, randint, sample
from itertools import permutations
import requests
from faker import Faker
from helpers import get_random_datetime
from datetime import datetime

MAX_IDEA_LENGTH = 140

USERS_CSV_HEADERS = ['email', 'username', 'image_url', 'password', 'user_type']
IDEAS_CSV_HEADERS = ['name', 'description', 'publish_date', 'url', 'privacy', 'user_id']
GROUPS_CSV_HEADERS = ['name']
KNOWLEDGE_SOURCES_CSV_HEADERS = ['name', 'text', 'publish_date', 'url', 'privacy', 'user_id']
KNOWLEDGE_DOMAINS_CSV_HEADERS = ['name']

NUM_USERS = 5
NUM_IDEAS = 10
NUM_GROUPS = 10
NUM_KNOWLEDGE_SOURCES = 10
NUM_KNOWLEDGE_DOMAINS = 10

fake = Faker()

# Generate random profile image URLs to use for users

image_urls = [
    f"https://randomuser.me/api/portraits/{kind}/{i}.jpg"
    for kind, count in [("lego", 10), ("men", 100), ("women", 100)]
    for i in range(count)
]

with open('generator/users.csv', 'w') as users_csv:
    users_writer = csv.DictWriter(users_csv, fieldnames=USERS_CSV_HEADERS)
    users_writer.writeheader()

    for i in range(NUM_USERS):
        users_writer.writerow(dict(
            email=fake.email(),
            username=fake.user_name(),
            image_url=choice(image_urls),
            password='mypass',
            user_type='admin',
        ))

with open('generator/ideas.csv', 'w') as ideas_csv:
    ideas_writer = csv.DictWriter(ideas_csv, fieldnames=IDEAS_CSV_HEADERS)
    ideas_writer.writeheader()

    for i in range(NUM_IDEAS):
        ideas_writer.writerow(dict(
            name=fake.paragraph()[:25],
            description=fake.paragraph()[:MAX_IDEA_LENGTH],
            publish_date=datetime.now(),
            url = fake.url(),
            privacy='private',
            user_id=randint(1, NUM_USERS),
        ))

with open('generator/groups.csv', 'w') as groups_csv:
    groups_writer = csv.DictWriter(groups_csv, fieldnames=GROUPS_CSV_HEADERS)
    groups_writer.writeheader()

    for i in range(NUM_GROUPS):
        groups_writer.writerow(dict(
            name=fake.paragraph()[:25],
        ))

with open('generator/knowledge_sources.csv', 'w') as knowledge_sources_csv:
    knowledge_sources_writer = csv.DictWriter(knowledge_sources_csv, fieldnames=KNOWLEDGE_SOURCES_CSV_HEADERS)
    knowledge_sources_writer.writeheader()

    for i in range(NUM_KNOWLEDGE_SOURCES):
        knowledge_sources_writer.writerow(dict(
            name=fake.paragraph()[:25],
            text=fake.paragraph()[:MAX_IDEA_LENGTH],
            publish_date=datetime.now(),
            url = fake.url(),
            privacy='private',
            user_id=randint(1, NUM_USERS),
        ))

with open('generator/knowledge_domains.csv', 'w') as knowledge_domains_csv:
    knowledge_domains_writer = csv.DictWriter(knowledge_domains_csv, fieldnames=KNOWLEDGE_DOMAINS_CSV_HEADERS)
    knowledge_domains_writer.writeheader()

    for i in range(NUM_KNOWLEDGE_DOMAINS):
        knowledge_domains_writer.writerow(dict(
            name=fake.paragraph()[:25],
        ))