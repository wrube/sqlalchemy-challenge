# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from pathlib import Path

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
db_path = Path.cwd() / Path('./Resources/hawaii.sqlite')

engine = create_engine(f"sqlite:///{db_path}")

# Declare a Base using `automap_base()`

Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Additional functions
#################################################
def temperature_obs(input_np_array):

    min_temp = input_np_array.min()
    max_temp = input_np_array.max()
    avg_temp = input_np_array.mean()

    return [min_temp, max_temp, avg_temp]



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all possible api routes
    """
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt or /api/v1.0/&ltstart&gt/&ltend&gt"
        
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """
    Generates precipitation data for the last year of data recordings in dictionary format with
    the key as the date and precipitation as the values.
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert all results to a dictionary with 
    all_precipitation = {}
    for row in results:
        all_precipitation[row[0]] = row[1]

    return jsonify(all_precipitation)

@app.route('/api/v1.0/stations')
def stations():
    """sumary_line
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    station_list = list(np.ravel(results))

    return jsonify(station_list)


@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    max_date = session.query(func.max(Measurement.date)).scalar()

    # extract the year, month and day from max_date as integers
    max_year, max_month, max_day = [int(i) for i in max_date.split('-')]

    # calculate the minimum date for query
    min_date = dt.date(max_year, max_month, max_day) - dt.timedelta(weeks=52)

    # Query to find the most active station in 

    # active_station = session.query(Measurement.station, func.count(Measurement.station).label('count'))\
    #                     .filter(Measurement.date >= min_date)\
    #                     .group_by(Measurement.station)\
    #                     .order_by(func.count(Measurement.station).desc())\
    #                     .first()
    
    # query to determine the most active station
    active_station = session.query(Measurement.station, func.count(Measurement.station).label('count'))\
                        .group_by(Measurement.station)\
                        .order_by(func.count(Measurement.station).desc())\
                        .first()[0]

    # query precipitation data for the last year of data collection
    results = session.query(Measurement.prcp)\
                .filter(Measurement.date >= min_date)\
                .filter(Measurement.station == active_station)\
                .all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def temperature_start_range(start):
    # Create our session (link) from Python to the DB


    session = Session(engine)


    results = session.query(Measurement.tobs).filter(Measurement.date >= start).all()

    session.close()

    results = np.ravel(results)

    temperature_stats = temperature_obs(results)

    return jsonify(temperature_stats)


@app.route('/api/v1.0/<start>/<end>')
def temperature_date_range(start, end):
    # Create our session (link) from Python to the DB

    session = Session(engine)

    results = session.query(Measurement.tobs).filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    results = np.ravel(results)

    temperature_stats = temperature_obs(results)

    return jsonify(temperature_stats)

    

if __name__ == '__main__':
    app.run(debug=True)
