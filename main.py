import json

from flask import Flask
from flask import request
from flask_cors import CORS
from omegaconf import OmegaConf

from core_lib.web_helpers.request_response_helpers import response_json
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/api/download_zip', methods=['POST'])
def send_message():
    conf = OmegaConf.create(request.json['config'])
    generator = CoreLibGenerator(conf)
    generator.run_all()
    return json.dumps({}), 200


if __name__ == '__main__':
    app.run()
