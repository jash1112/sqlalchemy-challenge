# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt



#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with= engine)

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
# 1. Home Page
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

# 2. /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    year1 = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    previous_last_date = dt.date(year1.year, year1.month, year1.day)

    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_last_date).order_by(Measurement.date).all()
    session.close()
    precipitation_dict = dict(results)

    print(f"Results for Precipitation - {precipitation_dict}")
    print("Out of Precipitation section.")
    return jsonify(precipitation_dict)

# 3. /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    station_query_result = session.query(*station_query).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in station_query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# 4. /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    tobs_query_result = session.query( Measurement.date, Measurement.tobs).\
    filter(Measurement.station=='USC00519281').\
    filter(Measurement.date>='2016-08-23').all()

    session.close()

    tob_obs = []
    for date, tobs in tobs_query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tob_obs.append(tobs_dict)

    return jsonify(tob_obs)

# 5.1 /api/v1.0/<start>
@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temperatures = []
    for min_temp, avg_temp, max_temp in start_results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temperatures.append(temps_dict)

    return jsonify(temperatures)

# 5.2 /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results_startEnd = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temperatures2 = []
    for min_temp, avg_temp, max_temp in results_startEnd:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temperatures2.append(temps_dict)

    return jsonify(temperatures2)


# Shows the debug tool to open and run the web app
if __name__ == "__main__":
    app.run(debug=True)