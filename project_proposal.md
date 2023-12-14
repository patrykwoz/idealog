# Project Proposal

## Idea


Application capturing, tracking research ideas, experiments, projects. Users can build relationships between the objects (ideas, paper, experiments, sketches).

## Get Started

|            | Description |
| ---------- | ----------- |
| Tech Stack | Python/Flask, PostgreSQL, SQLAlchemy, Heroku, Jinja, RESTful APIs, JavaScript, HTML, CSS, TForms, consider Bootstrap, Add Knowledge Base and Data Science related Technologies| 
| Type       | This is primarily a website app but designed to be viewed on mobile devices (responsive design).|
| Goal       | This project is designed to help its users create useful models of their research/ideas (knowledge graphs) and have full control over them. Additionally this project integrates LLM apis for predictive suggestions and enhanced semantic relationship building. On the UI side users can manipulate their ideas and assets using familiar and user friendly graph style interface. Connecting nodes (represent ideas) using wires (represent relationships), etc. |
| Users      | Designers, researchers, people who “process” many ideas during their workday and need a tool to help them build an ideas organization system. Thinking system. User types: admin, registered, guest.|
| Data       | I'm goiong to create my own API using user ideas and research articles they upload, but also tap into existing knowledge bases, e.g. [KBpedia](https://kbpedia.org/), datasets, e.g. Wikipedia, news articles, Hugging Face API for ML and Datasets|

# Project Breakdown

When planning your project, break down your project into smaller tasks, knowing that you may not know everything in advance and that these details might change later. Some common tasks might include:

- Determining the database schema
- Sourcing your data
- Determining user flow(s)
- Setting up the backend and database
- Setting up the frontend
- What functionality will your app include?
  - User login and sign up
  - Uploading a user profile picture

Here are a few examples to get you started with. During the proposal stage, you just need to create the tasks. Description and details can be edited at a later time. In addition, more tasks can be added in at a later time.

| Task Name | Description | Link to an Issue |
| --------- | ----------- | ---------------- |
| **APPLICATION DESIGN** | | |
| Design Database schema | Determine the models and database schema required for your project.  | [Link](https://example.com) |
| Determine Data Sources | Design data flows and resftul API. | [Link](https://exxample.com) |
| User Flows  | Determine user flow(s) - think about what you want a user’s experience to be like as they navigate your site. | [Link](https://example.com) |
| **SET UP BACKEND** | | |
| Set up Flask application | Create basic app structure. | [Link](https://example.com) |
| Create database and code models | SQL Database, Flask Models, WTF Forms | |
| Code user flows and authentication | | |
| Set up restful API | | |
| Build route for reading KS| Similar to the reading 'news'/'articles' Python library  | |
| Integrate KB | | |
| Create Templates | Integrate Graph Display Templates (Network) | |
| **SET UP FRONTEND** | | |
| Create simple UI | Simplest app interface for adding ideas and knowledge sources, groups,domains, tags,... | |
| User Login and Logout | | |
| Registered/Admin User View | | |
| Simple Display of KB graphs | | |
| Build all required user feature | See: Sketches | |
| Search, Grouping and Filtering Feature | | |
| Timeline Feature | | |
| Advanced Idea Relationships Display | User can select an idea and see its semantic tree - all ideas that it relates to, their text, url, artifacts | |
| Build Homepage | | |
| **SOURCE DATA** | | |
| Source data | Source data from existing apis and/or datasets and/or news articles | |
| Papers Upload | Let user upload pdfs with scientific papers and process them into Knowledge source | |
| *Better relationship extraction models | | |
| Workspace | *Setup frontend for miro-like canvas and graphs Styling | |


## Labeling

Labeling is a great way to separate out your tasks and to track progress. Here’s an [example](https://github.com/hatchways/sb-capstone-example/issues) of a list of issues that have labels associated.

| Label Type    | Description                                                                                                                                                                                                                                                                                                                     | Example                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| Difficulty    | Estimating the difficulty level will be helpful to determine if the project is unique and ready to be showcased as part of your portfolio - having a mix of task difficultlies will be essential.                                                                                                                               | Easy, Medium, Hard           |
| Type          | If a frontend/backend task is large at scale (for example: more than 100 additional lines or changes), it might be a good idea to separate these tasks out into their own individual task. If a feature is smaller at scale (not more than 10 files changed), labeling it as fullstack would be suitable to review all at once. | Frontend, Backend, Fullstack |
| Stretch Goals | You can also label certain tasks as stretch goals - as a nice to have, but not mandatory for completing this project.                                                                                                                                                                                                           | Must Have, Stretch Goal      |
