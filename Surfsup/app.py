# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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

# 1. /
#Start at the homepage.
#List all the available routes

@app.route("/")
def welcome():
    """Welcome to the Hawaii Climate Analysis API."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

# 2. /api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    one_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    last_date = dt.date(one_year.year,one_year.month,one_year.day)


    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_date).order_by(Measurement.date)

    p_dict = dict(results)

    print(f"Results for Precipitation - {p_dict}")
    print("Out of Precipitation section.")
    return jsonify(p_dict) 


# 3. /api/v1.0/stations
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    # Create a dictionary and append to the stations list
    stations = []
    for station,name,latitude,longitude,elevation in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = latitude
        station_dict["Lon"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

# 4. /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    queryresults = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').all()

    # Create a dictionary and append to the tobs_data list
    tobs_data = []
    for date, tobs in queryresults:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def start_temps(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary and append to the temps list
    temps = []
    for temp_min, temp_avg, temp_max in results:
        temps_dict = {}
        temps_dict["Minimum Temperature"] = temp_min
        temps_dict["Average Temperature"] = temp_avg
        temps_dict["Maximum Temperature"] = temp_max
        temps.append(temps_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temps(start, end): 
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

     # Create a dictionary and append to the temps list
    temps = []
    for temp_min, temp_avg, temp_max in results:
        temps_dict = {}
        temps_dict["Minimum Temperature"] = temp_min
        temps_dict["Average Temperature"] = temp_avg
        temps_dict["Maximum Temperature"] = temp_max
        temps.append(temps_dict)

    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)