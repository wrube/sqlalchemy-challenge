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
    """
    Returns the minimuum, maximum and average temperature of a given input 
    numpy array of temperatures.

    Args:
        input_np_array (numpy.array): Numeric 1D numpy array of observed temperatures

    Returns:
        list: 3 element list which returns [minimum, maximum, average] temperature
    """

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
    """
    The root page that Lists all possible api routes
    """
    return (
        f"Available Routes:<br/>"
        "<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt or /api/v1.0/&ltstart&gt/&ltend&gt"
        
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """
    Provides precipitation data for the last year of data recordings in dictionary format with
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
    """
    Provides station id data
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
    """Provides the temperature data for the last year of the station with the most number of observations
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # calculate the maximum date in the dataset
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

    # close the session
    session.close()

    # flatten the results
    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def temperature_start_range(start):
    """
    Returns the te observed temperatures statistics i.e. minimum temperature, maximum temperature and average temperature
    for a specified <start> date to the end of the dataset date range.

    Args:
        start (string): date string in the form "YYYY-MM-DD"

    Returns:
        JSON list: [minimum temp, maximum temp, average temp]
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query result that selects all temperature data after a given start date
    results = session.query(Measurement.tobs).filter(Measurement.date >= start).all()

    # close the session
    session.close()

    # flatten the results
    results = np.ravel(results)

    # calculate the temperature stats [minimum temp, maximum temp, average temp]
    temperature_stats = temperature_obs(results)

    return jsonify(temperature_stats)


@app.route('/api/v1.0/<start>/<end>')
def temperature_date_range(start, end):
    """
    Returns the te observed temperatures statistics i.e. minimum temperature, maximum temperature and average temperature
    for a specified <start> and <end> date range.

    Args:
        start (string): start date string in the form "YYYY-MM-DD"
        end (string): end date string in the form "YYYY-MM-DD"


    Returns:
        JSON list: [minimum temp, maximum temp, average temp]
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query result that selects all temperature data after a given start and end date
    results = session.query(Measurement.tobs).filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

     # close the session
    session.close()

    # flatten the results
    results = np.ravel(results)

    # calculate the temperature stats [minimum temp, maximum temp, average temp]
    temperature_stats = temperature_obs(results)

    return jsonify(temperature_stats)

    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
