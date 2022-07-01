sudo apt-get -y update
sudo apt-get -y upgrade 
sudo apt-get -y install ffmpeg
sudo apt-get -y install python3.10-venv
sudo apt-get -y install python3.10-dev
sudo apt-get -y install build-essential
sudo snap install blender --channel=3.2/stable --classic
mkdir -p /home/$USER/code
cd /home/$USER/code
git clone https://github.com/hovjdev/CyprusVitalSigns.git
python3 -m venv env
pip3 install --upgrade setuptools
pip3 install --upgrade pip
source env/bin/activate
cd CyprusVitalSigns
pip install -r requirements.txt



# dont forget to create a .env file, with your keys and tokens
# VIMEO_TOKEN=...
# VIMEO_ID=...
# VIMEO_SECRETS=...
# VIMEO_TOKEN=...
# VIMEO_ID=...
# VIMEO_SECRETS=...
# WEATHER_API_KEY=...