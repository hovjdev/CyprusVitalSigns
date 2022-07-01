source /home/$USER/code/env/bin/activate
cd /home/$USER/code/CyprusVitalSigns
git reset --hard
git pull
pip install -r requirements.txt
python cvs_create_data_vid.py

