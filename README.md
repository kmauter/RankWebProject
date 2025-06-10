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

## Game Creation
- [ ] User can add game description

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
- [ ] UI for description viewing

## Automation Between
- [X] When submission due date is passed, trigger Automation
- [X] Randomize order of songs
- [X] Create Spotify playlist (if given spotify account to make playlist in)
- [X] Create Youtube playlist (if given youtube account to make playlist in OR default account)
- [X] Switch stage to ranking

## Automation Additional Tasks
- [X] Update Game table to include playlist links
- [X] Remove song links from songs table
- [X] Add youtube/spotify account to user table for use in creating playlists
- [X] Create API endpoints for connecting user spotify and youtube
- [X] Set up Youtube OAuth Redirect
- [X] Set up Spotify OAuth Redirect
- [X] Update settings popup to use connection endpoints
- [X] Access user spotify and youtube tokens in automation task

## During Ranking Stage
- [ ] Player can see all songs/artists/comments
- [ ] Player can rank all songs
- [ ] Player can edit ranking 
- [ ] Player can save unfinished or finished rankings
- [ ] Owner can do all things Player can do AND
- [ ] Owner can edit the playlists if songs are incorrect (unless they did not give their account info)
- [ ] Owner can change rank due date
- [ ] Owner can remove player from game

## Ranking Additional Tasks
- [X] CRUD Ranking APIs
- [X] Drag and Drop UI
- [X] Style Drag and Drop
- [ ] Saving rankings button
- [ ] Save finished and partial rankings
- [ ] Load finished and partial rankings
- [ ] UI for Youtube and Spotify Playlists
- [ ] Songs don't refresh once loaded during ranking stage
- [ ] Mobile Friendly UI

## Automation Between
- [ ] When ranking due date is passed, trigger Automation
- [ ] Take all finished rankings (where all songs have been ranked)
- [ ] Remove the songs a user submitted from their ranking
- [ ] If a user submitted a song but did not rank, they cannot win. Make Red in results
- [ ] Calculate statistics for the game:
- [ ] Each song avg rank, median rank, range, controversy score, user who submitted

## During Finished Stage
- [ ] Display winner and winning song prominently!
- [ ] Display all songs, avg ranking and controversy score, and who submitted what
- [ ] Allow download for full data

## Deployment Setup and Development Processes
- [ ] Set up a cloud server (e.g., DigitalOcean Droplet) and connect via SSH
- [ ] Install all required software (Python, Node.js, Nginx, Git, etc.) on the server
- [ ] Clone the project repository onto the server
- [ ] Set up and activate a Python virtual environment for the backend
- [ ] Install backend dependencies and configure environment variables/secrets
- [ ] Build the frontend React app for production use
- [ ] Configure Flask to serve the built frontend files
- [ ] Set up Gunicorn to serve the Flask backend as a service
- [ ] Configure Nginx as a reverse proxy to Gunicorn for production traffic
- [ ] Set up a domain name and HTTPS with Let's Encrypt
- [ ] Test the deployed site to ensure all services are running correctly
- [ ] Set up Docker for consistent development and deployment environments
- [ ] Implement a CI/CD pipeline for automated testing and deployment
- [ ] Document any environment variables, secrets, or special setup steps for future development

## Stretch and QOL Features for Later
- [ ] UNIT TESTS
- [ ] Game creation includes choosing the submission limit
- [ ] Owner can delete the game
- [ ] Owner can set playlist name
- [ ] Modify all popups to use main-content format (settings, game creation, game joining)
- [ ] Upload Profile pictures for users
- [ ] Detailed User statistics
- [ ] Upload Game images for preview backgrounds?
- [ ] Add additional developers to the project (David, Spencer, Steph, Justin)
- [ ] Standardize font sizes
- [ ] Hover effects and increased visual feedback for interactions
- [ ] Email Verification
- [ ] Fetch additional song data from spotify (loudness, happiness, etc.) during first stage change
- [ ] Create a spreadsheet with all stats, ones given above and including additional song data from spotify during second stage change


### Goal POC Date: 8/1

# More Tasks

## Proper Documentation

## Security

## Deployment Notes

- If using a production WSGI server (e.g., Gunicorn), ensure the background scheduler in `app/tasks.py` runs only once (not per worker process). Consider running it as a separate service in production.

- Store client secrets and tokens securely (use environment variables).
- Use HTTPS in production.
- Never expose secrets to the frontend.

- Add your production domain’s redirect URI (e.g., https://yourdomain.com/api/spotifycallback) to the app’s Redirect URIs in spotify dashboard.
- Add your production domain’s redirect URI (e.g., https://yourdomain.com/api/youtubecallback) to the OAuth consent screen and credentials in google cloud console.
- Set env variables to correct production URIs
- In Google Cloud Console, publish your OAuth consent screen (move from "testing" to "production").
    - Complete the verification process (Google will require you to provide details, privacy policy, and may take several days to approve).
    - You may need to prove domain ownership and provide a privacy policy URL.
- Ensure your backend and frontend are served over HTTPS in production.
- Update any CORS settings to allow requests from your production frontend domain.
- For Google, once verified and in production, you can remove test users and allow public access.
- Proper logging for debugging purposes
- Allow users to submit bug reports