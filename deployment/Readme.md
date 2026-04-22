# Prod version deployment on AWS EC2.

Please find the latest version on https://github.com/FHNW-IGEO/Geoharvester/wiki/AWS-EC2

---

### Backup

Please check if there is a newer version available online!

# AWS EC2

## A. Set up instance from scratch

A rough howto that decribes the necessary steps to set up an EC2 instance and deploy Geoharvester to it. For connecting to a running instance (e.g. to update the code, see below)

### 1. Get an instance up and running

Requirements: Access to the AWS console, IAM Account . This needs to be provisioned by Swisstopo.

#### Configuration

- After login search for EC2 in the AWS Console.
- Choose "start instance"
- Assign servername, choose Linux based OS (either AWS Linux or Ubuntu)
- Pick free tier machine
- Pick your SSH key pair from the list (this is the same key that you should have locally on your PC, assigned by Swisstopo).
- Security group as is for now (can edit later)
- Up the memory to 16 GB (default is 8GB, but not sufficient for our app)
- Anything else, leave as default.
- Start the instance and wait a moment until it is flagged as "running".

#### Security rules

Set these security rules in the settings of your instance. Add more SSH IPs if your coworkers need access as well. Allow all IPs is discouraged for security concerns. Port 3000 is not really required, 8000 is needed for the backend.

![AWS_Security](https://user-images.githubusercontent.com/36440175/227956190-487f4aa3-3d0d-447b-bf5a-7b7a2dbea5ee.png)

#### Optional: Add your co-workers:

- Follow this guide: https://repost.aws/knowledge-center/new-user-accounts-linux-instance
- To get their public key (if it is in AWS already): Use AWS CLI and "describe key pairs" outlined here: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/describe-keys.html#retrieving-the-public-key
- Ask for their public ip (https://ip4.me/) and add it to the security settings (SSH)
- On the instance, copy your .ssh folder to /root: `sudo cp -r .ssh /root/.ssh`
- Add your coworkers public keys into /root/.ssh/authorized_keys
- Create a folder in /var, e.g. `mkdir /var/www`
- Change ownership so that all users can read & write: `sudo chmod -R 777 /var/www`. Use this folder to clone the repo (/var/www/Geoharvester and /var/www/html/react for the frontend)

#### Optional: Add a swapfile

If you encounter performance issues, a swapfile might help to take load of RAM:
https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-16-04

#### Optional: Assign Elastic IP

Note that this will change the IP of your instance (for SSH access)
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html#using-instance-addressing-eips-allocating

---

### 2. Connect to instance via SSH

- From a terminal: `~ ssh -i "swisstopo_key" ubuntu@ec2-<ip with "-" instead ".">.eu-central-1.compute.amazonaws.com`
- Swisstopo key is the one you created on your machine and have send to Swisstopo (private key, not .pub)
- If you connect from a folder diffrent from where the key is located, add the correct path.

---

### 3. Set up instance

Instance is like a fresh ubuntu machine, so all required dependencies need to be installed. For single access, you can use your home directory. If coworkers need access to the application, follow the "Add your coworkers" paragraph first (see above).

#### Git

- Generate ssh key on the instance then add it to your Github account
- See e.g. https://jdblischak.github.io/2014-09-18-chicago/novice/git/05-sshkeys.html
- Clone the repo to the instance.

#### Node

- Add node, npm and nvm
- See e.g. https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04
- From frontend folder run `npm run build` to build the frontend as static files.

#### Docker

- See e.g. https://docs.docker.com/engine/install/ubuntu/ for installation
- If you get a permission denied error when trying to start docker, follow this [guide](https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket):
- Exit the connection and reconnect to apply changes
- Start docker as described in readme to get the backend up and running
- To add your co-workers: https://www.configserverfirewall.com/ubuntu-linux/add-user-to-docker-group-ubuntu/

#### Nginx

- Install with `sudo apt install nginx`
- Add (new) config to `/etc/nginx/sites-enabled/` on instance
- Adjust the server name, it should be the public IP you get from AWS console
- Restart nxing to apply changes: `sudo service nginx restart`
- You can view the logs with `cat /var/log/nginx/error.log`

#### Frontend

We are not running the frontend as process (like you do during development) but instead serve static files with NGINX. Unfortunately we cannot use the build folder (see above) directly but have to copy the files to another location. **For frontend (code) updates** make sure to build the files and copy them to this new location, otherwise your update will not be reflected on the server.

- Create a new folder on the instance: `mkdir /var/www/html/react/`
- Copy files: `sudo cp -r /var/www/Geoharvester/client/build/* /var/www/html/react/`
- Set permissions: `chown -R www-data:www-data /var/www/html/react`

---

## B. Update code on an existing instance

Requirements: SSH access to the instance, have your (private) ssh key ready.
For more info see the details above.

### Locations on EC2:

- Frontend folder: **/var/www/html/react**
- Project / Backend folder: **/var/www/Geoharvester**
- Nginx config: **/etc/nginx/sites-enabled/Geoharvester_nginx** (A copy of the conf is found in the project folder)

### Connect

- From a terminal: `~ ssh -i "swisstopo_key" ubuntu@ec2-<ip with "-" instead ".">.eu-central-1.compute.amazonaws.com` (use your key name instead of "swisstopo_key")

### Add ssh key to your github repo

- Find the ssh key of the EC2 instance in the home directory, .ssh folder (`ls -la`)
- Add it to your github account (See last step here: https://jdblischak.github.io/2014-09-18-chicago/novice/git/05-sshkeys.html - do not create a new key, if there is one already)

### Update code

- Go to project / backend folder: **/var/www/Geoharvester**
- Pull code changes (git pull origin main)
- Backend: Restart docker (`docker compose up --build` from server folder)
- Frontend: Build & copy frontend (`npm run build` and `sudo cp -r /var/www/Geoharvester/client/build/* /var/www/html/react/`. Do not run the frontend as process (npm start), as static files are served with NGINX.
