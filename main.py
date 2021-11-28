from models.simulation import Simulation
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

simulation = Simulation(number_of_vehicles=1000)
frontend = True

@app.route('/simulation-state')
def simulation_state():
    simulation.step()
    return jsonify(simulation.to_json())


@app.route('/dead-spots')
def dead_spots():
    return []


if __name__ == '__main__':
    if frontend:
        app.run(debug=True)
    else:
        simulation.run()
