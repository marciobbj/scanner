# Argyle Test

This project tries at it's most to follow Clean Archtecture and Clean Code statements.

### Firstly, some choices I made:

This scanner is based on Selenium and Celery Task Queue. The main reason for Selenium is because the proposed web platform has some fancy tools to block simple scraping, so after some trials and fails I have decided to choose for a webdriver (firefox driver was picked since the chrome driver did not performed so well for the task) where I could run a headless browser with java
script enabled. Celery is because I am most familiarized with this tools than any other, I can easily debug tasks, also this is a very scalable choice where we can easily set our scan's rate, retries policies etc...

### Project architecture

The project is basically divided into 4 important pieces, the **Scanners** which are basically the "Client" for our services, they implement all logic for different web platforms one want to scan. Our **Entities**, composed by Pydantic Base Models to ease our data serialization. Our **Use Cases** with are the interface where we connect all this pieces together, they are Celery tasks that declares Scanners & Entities & Repositories. **Repositories** is where we place our adapters for our database/persistence tools.

### Running the project

### Unittests

Tests are located under `application/tests` and can be executed using `pytest application/tests -vv`
