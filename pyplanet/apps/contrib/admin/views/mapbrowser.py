import logging
import os
from argparse import Namespace
import re

from pyplanet.views.generics import ManualListView
from pyplanet.utils import gbxparser

logger = logging.getLogger(__name__)


class BrowserView(ManualListView):
	app = None
	title = 'Local Maps'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, app, player):
		super().__init__(self)
		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.objects_raw = []
		self.current_dir = ''

		self.fields = self.create_fields()

		self.sort_field = self.fields[2]

	async def set_dir(self, directory):
		self.objects_raw = list()
		self.current_dir = directory
		self.title = 'Local Maps     $n$aaa' + self.current_dir

		full_dir = os.path.join('UserData', 'Maps', self.current_dir)
		files = await self.app.instance.storage.driver.listdir(path=full_dir)

		self.objects_raw.append({'icon': '', 'file_name': '..', 'disabled': 1})

		# Add the files to the directory list.
		for file in files:
			is_file = await self.app.instance.storage.driver.is_file(os.path.join(full_dir, file))
			if is_file and not file.lower().endswith('map.gbx'):
				continue
			self.objects_raw.append({'icon': '' if is_file else '', 'disabled': 0 if is_file else 1, 'file_name': file})
		await self.display(player=self.player.login)

	def create_fields(self):
		return [
			{
				'name': '#',
				'index': 'disabled',
				'type': 'checkbox',
				'width': 6,
				'sorting': False,
			},
			{
				'name': ' ',
				'index': 'icon',
				'sorting': False,
				'width': 6,
				'type': 'label'
			},
			{
				'name': 'Name',
				'index': 'file_name',
				'sorting': True,
				'searching': True,
				'width': 150,
				'type': 'label',
				'action': self.action_file
			},
		]

	async def get_fields(self):
		return self.fields

	async def get_buttons(self):
		buttons = [
			{
				'title': ' Selected',
				'width': 20,
				'action': self.action_install_selected,
				'require_confirm': True
			}
		]
		return buttons

	async def action_file(self, player, values, instance, **kwargs):
		isdir = instance['icon'] == ''
		filename = instance['file_name']
		if isdir:
			if filename == '..':
				await self.set_dir(os.path.dirname(self.current_dir))
			else:
				await self.set_dir(os.path.join(self.current_dir, filename))
		else:
			await self.add_map(filename, player)

	async def action_install_selected(self, player, values, **kwargs):
		for key, value in values.items():
			if key.startswith('checkbox_') and value == '1':
				match = re.search('^checkbox_([0-9]+)_([0-9]+)$', key)
				if len(match.groups()) != 2:
					return

				row = int(match.group(1))
				await self.add_map(self.objects[row]['file_name'], player)

	async def add_map(self, filename, player):
		map_path = os.path.join(self.current_dir, filename)

		data = Namespace()
		data.map = map_path
		await self.app.map.add_local_map(player, data)
