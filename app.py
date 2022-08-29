from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

def get_weather_data(city):

    api_key = os.getenv('api_key')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    res = requests.get(url).json()
    return res

@app.route('/')
def index_get():
    
    cities = City.query.all()
    weather = []
    for city in cities:

        res = get_weather_data(city)
        
        data = {
            'name': city, 
            'temperature': res['main']['temp'],
            'description': res['weather'][0]['description'],
            'icon': res['weather'][0]['icon'],

        }

        weather.append(data)    

    return render_template('index.html', weather=weather)


@app.route('/', methods=['POST'])
def index_post():
        
    city_name = request.form['city_name']
    if city_name:

        exist = bool(City.query.filter_by(name=city_name).first())
        if not exist:

            new_city = get_weather_data(city_name)

            if new_city['cod'] == 200:
                city_obj = City(name=city_name)
                db.session.add(city_obj)
                db.session.commit()    
                flash('City added successfully', 'success')
            else:
                flash('Invalid data', 'error')

        else:
            flash('City already exists', 'error')

    
    return redirect(url_for('index_get')) 
    
@app.route('/delete/<city>')
def delete(city):
    city = City.query.filter_by(name=city).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'{city.name} deleted sucssefully', 'success')

    return redirect(url_for('index_get')) 


if __name__ == "__main__":
    app.run(debug=True)