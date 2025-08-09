# cloudbox
![Preview](images/design.png)

# APIs
- /upload
- /download
- /list_uploads
- /list_trash
- /delete : pending
- /restore : pending
- /status : pending

## more pending stuff
- metadata db
- jwt
- encryption
- blockchain
- chunking
- resetting password

## creating a sym link to allow using "cloudbox" as a cli tool
1. chmod +x /Users/ameyakhanzode/Desktop/New\ Learning/projects/cloud_project/cli.py
2. sudo ln -s /Users/ameyakhanzode/Desktop/New\ Learning/projects/cloud_project/cli.py /usr/local/bin/cloudbox

## make sure to create a database before using
1. psql -U your_username
2. CREATE DATABASE cloudbox;