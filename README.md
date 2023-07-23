README
Project Description
This project implements a script for processing data about calls and sending them to a telegram chat from API_MEGAFON. The script collects data on external and internal calls, saves the information to the SQLite database and sends notifications to the telegram chat.

How to start a project
Install the required dependencies listed in the requirements.txt file by running the following command:

pip install -r requirements.txt
Create an .env file in the root directory of the project and set the following environment variables in it:

API*TOKEN=<your_API*token*bot>
YOUR_CHAT_ID=<ID*of your*telegram*chat>

Run the main.py file to run the data processing script:

python main.py

How the project works

1. Data processing script (script.py)
   The script.py script provides classes and functions for handling call data.

CallDataProcessor class
CallDataProcessor is responsible for interacting with the SQLite database, processing data and sending POST requests to the specified site.
In the class constructor, you must pass the path to the SQLite database file where the customer numbers will be stored.
The create_table method creates the clients table in the database if it doesn't already exist.
The insert_client method adds a new client number to the database. If the number already exists, it is ignored.
The process_json_file method processes the data from the external JSON file and adds new customer numbers to the database.
Message_Json_Ex class
Message_Json_Ex is responsible for getting data about external calls.
The get_history method sends a request to an external API and gets call data for the current week. The data is then saved to a JSON file.
Message_Json_In class
Message_Json_In is responsible for getting data about internal calls.
The get_history method sends a request to the internal API and gets call data for the current week. The data is then saved to a JSON file.
Classes Call_Info_Ex and Call_Info_In
Call_Info_Ex and Call_Info_In are responsible for processing data on external and internal calls, respectively.
The check_and_send_message method checks new call data and sends a notification to the telegram chat about new calls.
The create_message method formats the call data into a human-readable message for sending to a telegram chat. 2. Sending notifications to telegram chat
To send notifications to a telegram chat, the aiogram library is used, which provides a convenient interface for working with the Telegram Bot API.
The bot.py file defines the send_data_to_chat function, which sends a text message or an audio file with call data to a telegram chat.
How to set up sending data to telegram chat
To send data to a telegram chat, you need to create your own bot in Telegram and get an API token. Then specify this token in the .env file, in the API_TOKEN variable.

Also specify the ID of your telegram chat in the YOUR_CHAT_ID variable.

Note
Before running the script, make sure you have access to API_MEGAFON

Author
Alximest
