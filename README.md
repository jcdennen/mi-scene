#Mi Scene - CIS 400 Social Media Mining project

This project uses the Twitter and Spotify APIs to lookup a Spotify Artist's top
Twitter followers with geographic information and plot the data in a Node.js
web app using the Google Maps Javascript API. All of the data is stored in a
local MongoDB instance.

##There are two main interactive parts to the project:

#### Part One:
1. Populate the MongoDB instance with data
  1. we must first install MongoDB (instructions below) and Python on our local machine
  2. we must then install the Twitter and Spotify Python libraries (for this we can simply use pip: "pip install spotipy" & "pip install twitter")
  3. We must import a Python module with proper Twitter credentials.
    + This will consist of assigning the correct keys to CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET
  4. Make sure that the artist you want to search has valid Spotify and Twitter accounts
    + The Twitter account should have at least 10,000 or so followers
    + While the more followers, the better data, keep in mind that it will take much longer mine data for these accounts
  5. Start up your local MongoDB instance with "mongod" within our project directory
  6. Run "python popular_followers.py" in a shell and follower the prompt
  7. Once your script is done running, we can check the MongoDB instance, by navigating to the /data/db directory and running the Mongo Shell with "mongo"
    + "db.influential_followers.find().pretty()" will show us all of our data formatted in a nice way
    + We can also search by artist or username by using find() with the following syntax: find({"Artist": "Basement"})

#### Part Two:
2. Display relevant data in the Node.js web app
  1. Once our database is populated, we should start up our local web app instance
  2. In a shell, move into the mi-scene directory, and type "npm install" to install appropriate dependencies
  3. Run the Node.js web application from the shell with the following command: "set DEBUG=mi-scene & npm start"
  4. The web application will be running live on port 3000: http://localhost:3000/
    + Occasionally there will be hiccups with the Google Maps displays. If there are any issues, simply reload the page until they resolve themselves.

###Installing MongoDB:
+ Detailed instructions for installing can be found here: [Mac](https://docs.mongodb.com/v3.2/tutorial/install-mongodb-on-os-x/), [Ubuntu](https://docs.mongodb.com/v3.2/tutorial/install-mongodb-on-ubuntu/), [Windows](https://docs.mongodb.com/v3.2/tutorial/install-mongodb-on-windows/)
+ Simply follow the instructions to download the most basic version of the Community Edition
  + SSL/TSL support is not necessary, and for safety do not install the latest development release
+ Make sure that the database is configured at 'mongodb://localhost:27017/test'
  + This is the URL that the Python scripts as well as the web app use to access the local MongoDB instance

###NOTE:
Master Branch contains final submission for CIS400 class, Working branch contains a version that is currently deemed "in progress"
