import importlib
import os

from pyplanet.conf.backends.base import ConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class FileConfigBackend(ConfigBackend):
	name = None
	files = None
	required_files = None

	def __init__(self, **options):
		super().__init__(**options)

		self.directory = None

	def load(self):
		# Make sure we load the defaults first.
		super().load()

		# Make sure we get the directory from the environment variable.
		self.directory = os.environ.get('PYPLANET_SETTINGS_DIRECTORY')

		if not self.directory:
			raise ImproperlyConfigured(
				'Settings directory is not defined! Please define PYPLANET_SETTINGS_DIRECTORY in your '
				'environment or start script (manage.py).'
			)

		# Make directory absolute.
		self.directory = os.path.join(os.getcwd(), self.directory)

		if not os.path.exists(self.directory) or not os.path.isdir(self.directory):
			raise ImproperlyConfigured(
				'Settings directory does not exist or is not a directory! Please define the right PYPLANET_SETTINGS_DIRECTORY '
				'in your environment or start script (manage.py).'
			)

		# Check for the two required files.
		if self.required_files:
			for req_file in self.required_files:
				file_path = os.path.join(self.directory, req_file)
				if not os.path.exists(file_path) or not os.path.isfile(file_path):
					raise ImproperlyConfigured(
						'One of the configuration files doesn\'t exist in the directory: '
						'file: {}'.format(req_file)
					)

		# Add the module itself to the configuration.
		self.settings['SETTINGS_DIRECTORY'] = self.directory

		# The rest should the parent class inherit and override!
