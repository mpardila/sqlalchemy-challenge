# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date  (e.g. /api/v1.0/2017-08-23)<br/>"
        f"/api/v1.0/start_date/end_date  (e.g. /api/v1.0/2017-08-01/2017-08-31)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Convert the query results from Precipitation analysis"""
    # Calculate the date one year from the last date in data set
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    last_year = session.query(Measurement.date, Measurement.station, Measurement.prcp).filter(Measurement.date >= query_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitations
    precipitations = []
    for date, station, prcp in last_year:
        precipitations_dict = {}
        precipitations_dict["Date"] = date
        precipitations_dict["Station"] = station
        precipitations_dict["Precipitation"] = prcp
        precipitations.append(precipitations_dict)

    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of all stations names"""
    # Query all stations
    stations = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations_names = list(np.ravel(stations))

    return jsonify(stations_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    """Query the dates and temperature observations of the most-active station for the previous year of data"""
    # Query the dates and temperature
    most_active_station = 'USC00519281'

    # Perform a query to retrieve the date and temperature observations scores of the most-active station
    mas_temp = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    mas_temperatures = []
    for station, date, tobs in mas_temp:
        mas_temperatures_dict = {}
        mas_temperatures_dict["Station"] = station
        mas_temperatures_dict["Date"] = date
        mas_temperatures_dict["Temperature"] = tobs
        mas_temperatures.append(mas_temperatures_dict)

    return jsonify(mas_temperatures)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date"""
    try:
        # Convert the start_date string to a datetime object for querying
        str_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = str_start_date.strftime("%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    
    session = Session(engine)

    # Perform a query to retrieve the temperature info based on the start_date
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_date).all()
    # Extract 'tobs' values for dates greater than or equal to start_date
    temperatures = [row.tobs for row in results]  

    session.close()

    if temperatures:
        # Calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start_date
        tmin = min(temperatures)
        tavg = sum(temperatures) / len(temperatures)
        tmax = max(temperatures)

        return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})
    else:
        return jsonify({"error": "No data available for the specified start date."}), 404

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_dates(start_date, end_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start and end date"""
    try:
        # Convert the start_date and end_date string to a datetime object for querying
        str_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = str_start_date.strftime("%Y-%m-%d")
        str_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = str_end_date.strftime("%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    
    session = Session(engine)

    # Perform a query to retrieve the temperature info based on the start_date and end_date
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    # Extract 'tobs' values for dates greater than or equal to start_date and end_date
    temperatures = [row.tobs for row in results]  

    session.close()

    if temperatures:
        # Calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start_date and end_date
        tmin = min(temperatures)
        tavg = sum(temperatures) / len(temperatures)
        tmax = max(temperatures)

        return jsonify({"TMIN": tmin, "TAVG": tavg, "TMAX": tmax})
    else:
        return jsonify({"error": "No data available for the specified start & end dates."}), 404

if __name__ == "__main__":
    app.run(debug=True)