# How to get your environment set up for local testing

## Part 1: Downloading the necessary programs

In order to build, run, and test this web project, the following programs must be downloaded.

- Visual Studio Code: https://code.visualstudio.com/download
- GitHub Desktop: https://github.com/apps/desktop
- Python 3.10: https://www.python.org/downloads/release/python-3100/
- Node JS: https://nodejs.org/en
- Dbeaver: https://dbeaver.io/download/
- Git: https://git-scm.com/downloads

## Part 2: Setting up the project

Now that you have the tools, you've got to put them to use.

1. Open GitHub Desktop and clone this repository
2. Open the repo in visual studio code
3. Install the extension donjayamanne.python-extension-pack
4. Click the python extension and click the + next to Workspace Environments
5. Select the python 3.10 as your interpreter from your system
6. Open a terminal in your new virtual environment by clicking open in terminal in the python extension
7. Execute the following command: pip install flask flask_sqlalchemy flask_migrate
8. Navigate to the client directory by executing: cd client
9. Execute the following command: npm install

## Part 3: Running the program

Now that you're all set up, let's run this thing.

1. Open two separate terminals, just like before
2. In the first, avigate to the client directory by executing: cd client
3. Now execute: npm start
4. In the other terminal execute: py run.py
5. It should be running now!

## Deployment Notes

- If using a production WSGI server (e.g., Gunicorn), ensure the background scheduler in `app/tasks.py` runs only once (not per worker process). Consider running it as a separate service in production.