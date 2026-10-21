"""`core_lib generate` asks about background jobs; each answer becomes a job of the library's YAML."""
import unittest

from core_lib_generator.config_collectors.job import generate_job_template
from tests.test_data.test_utils import typed


class TestJobCollector(unittest.TestCase):

    def test_job_runs_at_startup_and_once_by_default(self):
        # class name, initial delay [startup], frequency [Enter = none], another job [no]
        with typed('cleanup widgets', '', '', ''):
            jobs = generate_job_template('AcmeCoreLib')

        self.assertEqual(1, len(jobs))
        self.assertEqual('cleanup_widgets', jobs[0]['key'])
        self.assertEqual('0s', jobs[0]['initial_delay'])   # `startup` is stored as a zero delay
        self.assertEqual('', jobs[0]['frequency'])         # no frequency: the job runs once
        # The handler is the generated class `CleanupWidgets` in the library's `jobs/cleanup_widgets.py`.
        target = jobs[0]['handler']['_target_']
        self.assertTrue(target.startswith('acme_core_lib.'), target)
        self.assertTrue(target.endswith('.jobs.cleanup_widgets.CleanupWidgets'), target)

    def test_typed_schedule_and_a_taken_name_asked_again(self):
        with typed(
            'CleanupWidgets', '1h', '24h', 'yes',
            'cleanup_widgets', 'ArchiveWidgets', 'boot', '1h30m', 'no',   # `cleanup_widgets` is taken: asked again
        ):
            jobs = generate_job_template('AcmeCoreLib')

        self.assertEqual(
            [('cleanup_widgets', '1h', '24h'), ('archive_widgets', '0s', '1h30m')],
            [(job['key'], job['initial_delay'], job['frequency']) for job in jobs],
        )
        self.assertTrue(jobs[1]['handler']['_target_'].endswith('.jobs.archive_widgets.ArchiveWidgets'))
