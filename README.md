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

# Roadmap

## During Submission Stage
- [X] Player can submit a song
- [X] Player can delete a submitted song
- [X] Player can see their submitted songs
- [X] Player cannot submit more than a designated number of songs
- [X] Owner can do all things Player can do AND
- [X] Owner can see all songs submitted by any player in that game
- [X] Owner can delete any submitted song
- [X] Owner can NOT see who submitted what song
ALSO
- [X] Owner can change submission due date
- [X] Owner can change rank due date
- [X] Owner can remove player from game

## Submission Bug Tracker
- [X] When submitting a song, the song list is not updated
- [X] When submitting a song, if it is successful, it should clear the fields
- [X] Fix formatting on settings page to emphasize headers
- [X] User should get some feedback when saving the changed dates.

## Automation Between
- [ ] When submission due date is passed, trigger Automation
- [ ] Randomize order of songs
- [ ] Create Spotify playlist (if given spotify account to make playlist in)
- [ ] Create Youtube playlist (if given youtube account to make playlist in OR default account)
- [ ] Switch stage to ranking
- [ ] Fetch additional song data from spotify (loudness, happiness, etc.)

## Automation Bug Tracker
- [ ] Update Game table to include playlist links
- [ ] Remove song links from songs table
- [ ] Add youtube/spotify account to user table for use in creating playlists

## During Ranking Stage
- [ ] Player can see all songs/artists/comments
- [ ] Player can rank all songs
- [ ] Player can edit ranking 
- [ ] Player can save unfinished or finished rankings
- [ ] Owner can do all things Player can do AND
- [ ] Owner can edit the playlists if songs are incorrect (unless they did not give their account info)
- [ ] Owner can change rank due date
- [ ] Owner can remove player from game

## Automation Between
- [ ] When ranking due date is passed, trigger Automation
- [ ] Take all finished rankings (where all songs have been ranked)
- [ ] Remove the songs a user submitted from their ranking
- [ ] If a user submitted a song but did not rank, they cannot win. Make Red in results
- [ ] Calculate statistics for the game:
- [ ] Each song avg rank, median rank, range, controversy score, user who submitted
- [ ] Create a spreadsheet with all stats, ones given above and including additional song data from spotify

## During Finished Stage
- [ ] Display winner and winning song prominently!
- [ ] Display all songs, avg ranking and controversy score, and who submitted what
- [ ] Allow download for full data

## Stretch and QOL Features for Later
- [ ] Game creation includes choosing the submission limit
- [ ] Owner can delete the game
- [ ] Owner can set playlist name
- [ ] Modify game creation UI to match main-content format
- [ ] Modify game joining UI to match main-content format

# Deployment Notes

- If using a production WSGI server (e.g., Gunicorn), ensure the background scheduler in `app/tasks.py` runs only once (not per worker process). Consider running it as a separate service in production.