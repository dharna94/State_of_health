from flask import Flask
from SOH_API.soh_main import SOH_MAIN_

app = Flask(__name__)

base_url = '/api/soh_calculation'

# Registering the score blueprint
app.register_blueprint(SOH_MAIN_, url_prefix = base_url+"/soh")

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')