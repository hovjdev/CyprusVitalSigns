cd /home/$USER/code
source env/bin/activate
cd /home/$USER/code/CyprusVitalSigns
git pull
pip install -r requirements.txt
python cvs_create_data_vid.py
