## After installing a new dependancy you need to add it to the requirements.txt before deploying to heruko
pip freeze > requirements.txt

Start Envrionment while in your_tackle
source ./env/Scripts/activate 

Start Heroku Dyno after deploying  
heroku ps:scale web=1
