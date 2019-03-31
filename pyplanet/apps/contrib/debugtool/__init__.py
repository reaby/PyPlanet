"""
Clock
"""
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command


class Debugtool(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='connect', target=self.add_fake_player, perms='admin:reboot', admin=True).add_param(
				'amount', nargs='1', type=str, required=True, help='amount of fake players to add'),
			Command(command='disconnect', target=self.remove_fake_player, perms='admin:reboot', admin=True),
		)

	async def add_fake_player(self, player, data, **kwargs):
		amount = int(data.amount)
		self.instance.chat("$fffAdding {} fake players".format(amount))
		for i in range(0, amount):
			await self.instance.gbx("ConnectFakePlayer")

	async def remove_fake_player(self, player, data, **kwargs):
		self.instance.chat("$fffRemoving all fake players")
		await self.instance.gbx("DisconnectFakePlayer", "*")
