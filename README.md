## Features

* Users can tag the name of the bot and the name of the person they traded with in their trade thread to invoke the bot. When the tagged user replies to the comment with "confirmed" the bot will reply with "added" and give them credit.

* Users can send a message to the bot with u/<some_username> in the body of the message to get the feedback score for that person.

## Basic Run Instructions

* Clone this repository using `git clone`

* Replace subreddit_name with the name of your subreddit at the top of swap.py

* Create a `config.txt` file with these four attributes, in this order, each on their own line (the .gitignore will prevent you from uploading this file to the repo):

    * The name of the subreddit you want to run on e.g. `funkoswap`

    * Reddit API client ID

    * Reddit API client secret

    * Reddit Bot Username

    * Reddit Bot Password
    
* Create the data files using 

    * `> database/swaps-funkoswap.json`
    
    * `> database/active_comments-funkoswap.txt`

* Create a config file in the config directory named `funkoswap-config.txt` with the following on seperate lines:

    * Subreddit name
    
    * Bot Client ID
    
    * Bot Secret ID
    
    * Bot Username
    
    * Bot Password
    
    * User Flair Text (defaults to Swaps)
    
    * Moderator Flair Text (defaults to empty string)

* Add the following cronjob using `crontab -e` 

    * `\* \* \* \* \* cd ~/<YOUR_DIRECTORY_NAME> & python swap.py funkoswap-config.txt;`
    
## Using Git to back up the Data Files

Because this script uses json files to store the data, it can be useful to have a backup of the data somewhere. Git is convenient for this. By creating your own github repository, you can push your data files to the remote server once an hour to ensure proper back up and be able to recover should anything go wrong. Follow these steps to do so:

* Create your own directory for your version of the script and move all visible files (files that do not start with a `.`) and the .gitignore to the new directory.

* Initialize the directory as a new git repository (this assumes you are already signed in to git on your machine).

* Add the following cronjob to your server with `crontab -e` to enable creating hourly backups of the data files:

    * `0 * * * * cd ~/<YOUR_DIRECTORY_NAME> && git pull; git add *; git commit -m "hourly upload"; git push;`

## Legacy Trades

The code references Legacy Trades. These are confirmed trades from before you bring the bot online. 
It recognizes a legacy trade only if it appears in the database file. 
If you have no record of trades before bringing this bot online, you can ignore legacy trades. 
If you wish to give credit to your users from their legacy trades, you will have to write your own script to do so. 
The general idea is to write entries in the json file for username: ["LEGACY TRADE", "LEGACY TRADE"] for as many legacy trades as that person had. 
Once you have the backfilled json file in the database folder, the script will use those legacy trades when showcasing the user reputation

