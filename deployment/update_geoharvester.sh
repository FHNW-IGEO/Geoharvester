# This script simplifies updating of the geoharvester project. Copy it to and run it from the home directory of your AWS instance.
# If you perfer to update manually, follow the documentation at: https://github.com/FHNW-IGEO/Geoharvester/wiki/AWS-EC2
# For debugging, make sure that the target folders exist at the indicated paths.

cd /var/www/Geoharvester/server
docker compose down
cd ../
git pull origin main
cd ./server
docker compose up --build -d
cd ../client
npm run build
sudo cp -r /var/www/Geoharvester/client/build/* /var/www/html/react/
echo "(!) Done updating. Please verify that everything works as intended. (!)"