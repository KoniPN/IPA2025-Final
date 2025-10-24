#######################################################################################
# Yourname: Pisit Ngamlertpatanasiri
# Your student ID: 66070136
# Your GitHub Repo: https://github.com/KoniPN/IPA2024-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
import restconf_final
import netconf_final
import netmiko_final
import ansible_final
import glob

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
# IPA2025 Webex Teams room ID
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

# Change this to your student ID
STUDENT_ID = "66070136"

# Variable to store the selected method (restconf or netconf)
selected_method = None

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": "Bearer " + ACCESS_TOKEN}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space
    if message.startswith(f"/{STUDENT_ID} "):

        # Split the message to extract components
        message_parts = message.split(" ")
        
        # Define allowed router IPs and methods
        ALLOWED_IPS = ["10.0.15.61", "10.0.15.62", "10.0.15.63", "10.0.15.64", "10.0.15.65"]
        ALLOWED_METHODS = ["restconf", "netconf"]
        PART1_COMMANDS = ["create", "delete", "enable", "disable", "status"]
        PART2_COMMANDS = ["gigabit_status", "showrun", "motd"]
        
        router_ip = None
        command = None
        motd_text = None
        responseMessage = None
        
        # Parse message based on different formats
        if len(message_parts) == 2:
            # Format: /studentID <method> OR /studentID <IP> OR /studentID <command>
            second_part = message_parts[1]
            
            if second_part in ALLOWED_METHODS:
                # Method selection: /66070136 restconf or /66070136 netconf
                selected_method = second_part
                responseMessage = f"Ok: {second_part.capitalize()}"
            elif second_part in ALLOWED_IPS:
                # IP without command: /66070136 10.0.15.65
                router_ip = second_part
                responseMessage = "Error: No command found."
            else:
                # Command without method or IP: /66070136 create
                if selected_method is None:
                    responseMessage = "Error: No method specified"
                else:
                    responseMessage = "Error: No IP specified"
                    
        elif len(message_parts) == 3:
            # Format: /studentID <IP> <command>
            second_part = message_parts[1]
            third_part = message_parts[2]
            
            if second_part in ALLOWED_IPS:
                router_ip = second_part
                command = third_part
            else:
                # Invalid format
                responseMessage = "Error: No command found"
                
        elif len(message_parts) >= 4:
            # Format: /studentID <IP> <command> <additional text>
            # This is for motd command with text
            second_part = message_parts[1]
            third_part = message_parts[2]
            
            if second_part in ALLOWED_IPS:
                router_ip = second_part
                command = third_part
                # Get remaining text (for MOTD)
                motd_text = ' '.join(message_parts[3:])
            else:
                # Invalid format
                responseMessage = "Error: No command found."
        else:
            # Invalid format
            responseMessage = "Error: No command found."
            
        print(f"Method: {selected_method}, Router IP: {router_ip}, Command: {command}, MOTD Text: {motd_text}")

# 5. Complete the logic for each command

        # Only execute command if responseMessage is not already set
        if responseMessage is None:
            if router_ip is None or command is None:
                # If method is selected but missing command
                if router_ip is not None and command is None:
                    responseMessage = "Error: No command found."
                elif selected_method is None:
                    responseMessage = "Error: No method specified"
                else:
                    responseMessage = "Error: No IP specified"
            elif command in PART1_COMMANDS:
                # Part 1 commands - need method selection
                if selected_method is None:
                    responseMessage = "Error: No method specified"
                elif selected_method == "restconf":
                    if command == "create":
                        responseMessage = restconf_final.create(router_ip)
                    elif command == "delete":
                        responseMessage = restconf_final.delete(router_ip)
                    elif command == "enable":
                        responseMessage = restconf_final.enable(router_ip)
                    elif command == "disable":
                        responseMessage = restconf_final.disable(router_ip)
                    elif command == "status":
                        responseMessage = restconf_final.status(router_ip)
                elif selected_method == "netconf":
                    if command == "create":
                        responseMessage = netconf_final.create(router_ip)
                    elif command == "delete":
                        responseMessage = netconf_final.delete(router_ip)
                    elif command == "enable":
                        responseMessage = netconf_final.enable(router_ip)
                    elif command == "disable":
                        responseMessage = netconf_final.disable(router_ip)
                    elif command == "status":
                        responseMessage = netconf_final.status(router_ip)
            elif command in PART2_COMMANDS:
                # Part 2 commands - don't need method selection
                if command == "gigabit_status":
                    responseMessage = netmiko_final.gigabit_status(router_ip)
                elif command == "showrun":
                    responseMessage = ansible_final.showrun(router_ip)
                elif command == "motd":
                    # Check if setting or getting MOTD based on whether text is provided
                    if motd_text:
                        # Has text = Set MOTD using Ansible
                        responseMessage = netmiko_final.set_motd(router_ip, motd_text)
                    else:
                        # No text = Get MOTD using Netmiko
                        responseMessage = netmiko_final.get_motd(router_ip)
            else:
                responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if command == "showrun" and responseMessage == 'ok':
            # Find the generated file
            pattern = f"show_run_{STUDENT_ID}_*.txt"
            files = glob.glob(pattern)
            if files:
                filename = files[0]  # Get the first matching file
                fileobject = open(filename, 'rb')
                filetype = "text/plain"
                postData = {
                    "roomId": roomIdToGetMessages,
                    "text": "show running config",
                    "files": (filename, fileobject, filetype),
                }
                postData = MultipartEncoder(postData)
                HTTPHeaders = {
                    "Authorization": "Bearer " + ACCESS_TOKEN,
                    "Content-Type": postData.content_type,
                }
            else:
                # File not found, send error message
                postData = {"roomId": roomIdToGetMessages, "text": "Error: Config file not found"}
                postData = json.dumps(postData)
                HTTPHeaders = {"Authorization": "Bearer " + ACCESS_TOKEN, "Content-Type": "application/json"}
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": "Bearer " + ACCESS_TOKEN, "Content-Type": "application/json"}   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
