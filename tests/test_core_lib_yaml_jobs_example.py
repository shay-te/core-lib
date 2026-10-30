"""The commented `jobs:` example in core_lib/config/core_lib.yaml is a shape load_jobs() accepts."""
import os
import unittest

import yaml
from omegaconf import OmegaConf

from core_lib.core_lib import CoreLib
from core_lib.jobs.job import Job

CORE_LIB_YAML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core_lib', 'config', 'core_lib.yaml'
)


class ExampleJob(Job):
    instances = []

    def __init__(self, some_param: str = None):
        self.some_param = some_param
        self.data_handler = None
        ExampleJob.instances.append(self)

    def initialized(self, data_handler):
        self.data_handler = data_handler

    def run(self):
        pass


class ExampleCoreLib(CoreLib):
    def __init__(self):
        super().__init__()


def commented_jobs_example() -> dict:
    with open(CORE_LIB_YAML) as yaml_file:
        lines = yaml_file.read().splitlines()
    start = lines.index('#  jobs:')
    block = []
    for line in lines[start:]:
        if not line.startswith('#'):
            break
        block.append(line[1:])
    return yaml.safe_load('\n'.join(block))['jobs']


class TestCoreLibYamlJobsExample(unittest.TestCase):

    def setUp(self):
        ExampleJob.instances = []

    def tearDown(self):
        for job in ExampleJob.instances:
            CoreLib.scheduler.stop(job)

    def test_load_jobs_accepts_the_example(self):
        jobs = commented_jobs_example()
        job_name = next(iter(jobs))
        self.assertIn('_target_', jobs[job_name]['handler'])  # the example's own class, swapped for a test job
        jobs[job_name]['handler']['_target_'] = f'{__name__}.{ExampleJob.__qualname__}'
        example_core_lib = ExampleCoreLib()

        example_core_lib.load_jobs(OmegaConf.create(jobs), {job_name: example_core_lib})

        self.assertEqual(1, len(ExampleJob.instances))
        job = ExampleJob.instances[0]
        self.assertEqual('some value', job.some_param)
        self.assertIs(example_core_lib, job.data_handler)
