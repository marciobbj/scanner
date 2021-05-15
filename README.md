# Argyle Test

This project tries at it's most to follow Clean Architecture and Clean Code statements.

### Choices I made:

This scanner is based on Selenium and Celery Task Queue. The main reason for Selenium is because the proposed web platform has some fancy tools to block simple scraping, so after some trials and fails I have decided to choose for a webdriver (firefox driver was picked since the chrome driver did not performed so well for the task) where I could run a headless browser with java
script enabled. Celery is because I am most familiarized with this tool, I can easily debug tasks, also this is a solid and scalable choice where we can easily set our scanners task rate, have fine control over retries policies etc...

### Project architecture

The project is basically divided into 4 important pieces, the **Scanners** which are basically the "Client" for our services, they implement all logic for different web platforms one want to scan. Our **Entities**, composed by Pydantic Base Models to ease our data serialization. Our **Use Cases** which are the interfaces where we connect all these pieces together, they are Celery tasks that declares Scanners & Entities & Repositories. **Repositories** is where we place our adapters for our database/persistence tools.

### Ways to run the Scanner
There is two ways of running this project, one is using Celery Task Queue, and the other is running the scanner as is, blocking the thread with no fancy concurrent things going on. The first one is more efficient and proper for production environments, the second one is made for testing & development purpose and for simplicity. In the next lines I will go through on how to run the project in both situations.

**Please, before continue make sure Mozilla Firefox is installed on your machine, since the Scanner uses Firefox webdriver, it is a requirement.**

### 1. Installing test/dev version locally
Install the dependecies in a python>=3.8.0 environment, in the root folder just do:
- `(python3.8) $ pip install -r requirements.txt`

At this point you are good to go for running the scanner in a simpler way, in the root folder one can do:
- `(python3.8) $ python -m run`

_The above command with run the scanner locally, without any of the Celery advantages._

### 1.1 Installing the complete version locally
For the complete version we will need to setup a few things before running, for this project I picked Redis to work with Celery. I recommend installing Docker in your environment since it will give an up and running version of Redis in no time, reference on how to install [here](https://docs.docker.com/engine/install/ubuntu/). With Docker installed in your terminal type: 

- `(python3.8) $ docker run --name redis -p 6379:6379 -d redis`

Now you have a nice version of Redis installed in your machine. The next step is to run our Celery Worker, one can do this by:

- `(python3.8) $ celery -A application worker --loglevel=INFO`

After running the worker you can leave it there and open another tab in your terminal. This project comes with a fancy version of the pythons IDLE, it is called ipython. For starting test our worker we will do:

### 1.2 Running the Scanner
- `(python3.8) $ ipython`
- `In [1]: from run import main`
- `In [2]: main({'username': 'bobsuperworker', 'password': 'Argyleawesome123!'}, _async=True)`

In your worker, if you were successful you will a some log like these:

```
[2021-05-15 10:55:14,633: INFO/MainProcess] Received task: application.use_cases.scan_upwork_main_page[562b21b3-17a0-46c9-a440-4504e13a0dcf]
[2021-05-15 10:55:14,635: INFO/ForkPoolWorker-4] application.use_cases.scan_upwork_main_page[562b21b3-17a0-46c9-a440-4504e13a0dcf]: starting task to scan upwork main page
```

### Unittests

Tests are located under `application/tests` and can be executed using `pytest application/tests -vv`
