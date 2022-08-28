from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

@app.route('/', methods=['GET', 'POST'])
def index():
        
        if request.method == 'POST':
            city_name = request.form['city_name']
            if city_name:
                city_obj = City(name=city_name)
                db.session.add(city_obj)
                db.session.commit()    


        cities = City.query.all()
        weather = []
        for city in cities:
            url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(city, os.getenv('api_key'))
            res = requests.get(url).json()
            
            data = {
                'name': city, 
                'temperature': res['main']['temp'],
                'description': res['weather'][0]['description'],
                'icon': res['weather'][0]['icon'],

            }

            weather.append(data)    

        return render_template('index.html', weather=weather)
       

if __name__ == "__main__":
    app.run(debug=True)