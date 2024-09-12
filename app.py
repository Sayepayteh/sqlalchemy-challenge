# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"- Returns prior year rain totals from all stations<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"- Returns a list of all station numbers and names<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"- Returns the prior year temperatures from all stations<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/start'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"- Returns MIN/AVG/MAX temperature for dates greater than or equal to the start date<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/start/end'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a><br/>"
        f"- Returns MIN/AVG/MAX temperature between the start and end date inclusive<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Convert to datetime and subtract one year
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=366)

    # Query for precipitation data from the last year
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Create a list of dictionaries using a list comprehension
    precip_data_totals = [{"date": date, "prcp": prcp} for date, prcp in precip_data]

    return jsonify(precip_data_totals)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station).all()
    
    # Create a list of dictionaries with station name and station code
    stations = [{"name": name, "station": station} for name, station in stations_query]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Convert to datetime and subtract one year
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=366)

    # Query for temperature data from the last year
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > one_year_ago).\
        order_by(Measurement.date).all()

    # Create a list of dictionaries with `date` and `tobs` as the keys and values
    temp_totals = [{"date": result[0], "tobs": result[1]} for result in temperature]

    return jsonify(temp_totals)

@app.route("/api/v1.0/<start>")
def trip1(start):
    # Query for Min/Avg/Max temperature from the start date to the end of the data set
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.date(2017, 8, 23)

    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end).all()

    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start, end):
    # Query for Min/Avg/Max temperature between the start and end dates
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    trip = list(np.ravel(trip_data))
    return jsonify(trip)

if __name__ == "__main__":
    app.run(debug=True)
