import os


broker_url = os.getenv("BROKER_URL", "redis://localhost:6379")

imports = "application.use_cases.upwork.tasks"

# task messages will be acknowledged after the task has been executed
task_acks_late = True
