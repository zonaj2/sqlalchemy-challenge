# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement =Base.classes.measurement
Station=Base.classes.station

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Startdate/&lt;Startdate&gt;<br/>"
        f"/api/v1.0/Startdate_Enddate/&lt;Startdate&gt;/&lt;Enddate&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of last 12 months of precipitation data"""
    # Query precip data
    results = session.query(Measurement.date, Measurement.prcp) \
    .filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").all()

    session.close()
   #Convert the query results to a dictionary using date as the key and prcp as the value.
    all_dates = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_dates.append(precip_dict)
    
    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)
    # Query stations
    results2 = session.query(Station.station).all()
    
    session.close()
    # Convert list into normal list
    all_stations = list(np.ravel(results2))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)
    #Query tobs for USC00519281 for previous year
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").\
    order_by(Measurement.date).all()

    all_temps = []
    for date, tobs in results:
        temp_dict ={}
        temp_dict["date"]= date
        temp_dict["temperature observation"] = tobs
        all_temps.append(temp_dict)

    return jsonify(all_temps)



@app.route("/api/v1.0/Startdate/<Startdate>")
def start_dt(Startdate):
    session = Session(engine)

    # Query temperature data for dates greater than or equal to start_date
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= Startdate).all()

    session.close()

    temperature_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    if temperature_data:
        # Calculate temperature statistics
        temperatures = [entry["temperature"] for entry in temperature_data]

        min_temp = min(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)

        temperature_statistics = {
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }

        return jsonify(temperature_statistics)
    else:
        return jsonify({"error": f"No temperature data available for the provided start date {Startdate}."}), 404

@app.route("/api/v1.0/Startdate_Enddate/<Startdate>/<Enddate>")
def start_end_dt(Startdate, Enddate):
    session = Session(engine)

    # Query temperature data for dates greater than or equal to start date and less than or equal to end date
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= Startdate).\
        filter(Measurement.date <= Enddate).all()

    session.close()
    temperature_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    if temperature_data:
        # Calculate temperature statistics
        temperatures = [entry["temperature"] for entry in temperature_data]

        min_temp = min(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)

        temperature_statistics = {
            "TMIN": min_temp,
            "TAVG": avg_temp,
            "TMAX": max_temp
        }

        return jsonify(temperature_statistics)


if __name__ == '__main__':
    app.run(debug=True)