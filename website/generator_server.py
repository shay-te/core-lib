import io
import os
import shutil

import hydra
from flask import Flask, Response
from flask import request
from flask_cors import CORS
from hydra import initialize_config_dir, compose
from omegaconf import OmegaConf
from tempfile import TemporaryDirectory

from core_lib.helpers.string import camel_to_snake
from core_lib_generator.core_lib_generator_from_yaml import CoreLibGenerator

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_archive_content(config: dict):
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    conf = OmegaConf.create(config)
    cwd = os.getcwd()
    with TemporaryDirectory() as temp_dir:
        cl_name = conf.core_lib.name
        cl_snake_name = camel_to_snake(cl_name)
        with open(f'{temp_dir}/{cl_name}.yaml', 'w+') as file:
            OmegaConf.save(config=conf, f=file.name)
        os.chdir(temp_dir)
        initialize_config_dir(config_dir=os.getcwd())
        CoreLibGenerator(compose(cl_name)).run_all()
        core_lib_dir_path = os.path.join(temp_dir, cl_snake_name)
        shutil.make_archive(cl_snake_name, 'zip', core_lib_dir_path)
        os.chdir(cwd)
        with open(os.path.join(temp_dir, f'{cl_snake_name}.zip'), "rb") as f:
            content = io.BytesIO(f.read())
            return content


@app.route('/api/download_zip', methods=['POST'])
def download_zip():
    archive = get_archive_content(request.json['config'])
    return Response(archive, mimetype='application/zip',
                    headers={'Content-Disposition': 'attachment;filename=core_lib.zip'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
