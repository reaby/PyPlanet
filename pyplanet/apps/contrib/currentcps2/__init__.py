import logging

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from .view import CPWidgetView


class CurrentCPs(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.widget = None

	async def on_start(self, *args, **kwargs):
		# Listen to some signals
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.map.map_begin, self.map_begin)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)

		# Make sure we move the rounds_scores and other gui elements.
		self.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 87. 150.')
		self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')

		self.widget = CPWidgetView(self)
		# await self.widget.display()
		await self.widget.display()

	# When a player connects
	async def player_connect(self, player, *args, **kwargs):
		await self.widget.display(player)

	async def map_begin(self, *args, **kwargs):
		await self.widget.display()

	async def podium_start(self, *args, **kwargs):
		await self.widget.hide()
