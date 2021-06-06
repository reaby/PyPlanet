from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.contrib.players.views import PlayerListView
from pyplanet.apps.core.maniaplanet.callbacks import player as player_signals
from pyplanet.contrib.player.exceptions import PlayerNotFound
from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.maniaplanet.models import Player as PlayerModel


class Players(AppConfig):
	name = 'pyplanet.apps.contrib.players'
	game_dependencies = ['trackmania', 'trackmania_next', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setting_enable_join_msg = Setting(
			'enable_join_message', 'Enable player join messages', Setting.CAT_FEATURES, type=bool, default=True,
			description='Enable this to announce that a player has joined the server.'
		)
		self.setting_enable_leave_msg = Setting(
			'enable_leave_message', 'Enable player leave messages', Setting.CAT_FEATURES, type=bool, default=True,
			description='Enable this to announce that a player has left the server.'
		)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='players', target=self.player_list, description='Displays the list of players currently online.'),
			Command(command='laston', aliases=['lastseen'], target=self.command_laston,
					description='Displays the last time the provided player was online on this server.').add_param(name='login', required=True),
			Command(command='setname', target=self.command_setname,
					description='Sets custom nickname').add_param(name="name", required=False)
		)
		await self.context.setting.register(
			self.setting_enable_join_msg, self.setting_enable_leave_msg
		)

		player_signals.player_connect.register(self.player_connect)
		player_signals.player_disconnect.register(self.player_disconnect)

	async def player_list(self, player, data, **kwargs):
		view = PlayerListView(self)
		await view.display(player=player.login)

	async def command_laston(self, player, data, **kwargs):
		try:
			laston_player = await self.instance.player_manager.get_player(data.login, None, False)
			if laston_player.last_seen is not None:
				message = '$ff0Player $fff{}$z$s$ff0 was last online on $fff{}$ff0 at $fff{}$ff0.'.format(laston_player.nickname, laston_player.last_seen.strftime('%d-%m-%Y'), laston_player.last_seen.strftime('%H:%M:%S'))
				await self.instance.chat(message, player)
			else:
				message = '$ff0Player $fff{}$z$s$ff0 has not been seen online (yet).'.format(laston_player.nickname)
				await self.instance.chat(message, player)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def command_setname(self, player, data, **kwargs):
		try:
			db_player = await PlayerModel.get_by_login(player.login)
			if db_player is not None:
				if data.name is not None:
					old_nickname = player.nickname
					db_player.nickname = data.name
					db_player.nickname_override = True
					await db_player.save()
					await self.instance.player_manager.handle_disconnect(player.login)
					await self.instance.player_manager.handle_connect(player.login)
					message = '$ff0Player $fff{}$z$s$ff0 is now known as $fff{}$z$s$ff0.'.format(old_nickname, data.name)
					await self.instance.chat(message, player)
				else:
					message = '$ff0Nickname reverted to default.'
					db_player.nickname_override = False
					await db_player.save()
					await self.instance.player_manager.handle_disconnect(player.login)
					await self.instance.player_manager.handle_connect(player.login)
					await self.instance.chat(message, player)
		except PlayerNotFound:
			message = '$i$f00 player not found.'

			await self.instance.chat(message, player)

	async def player_connect(self, player, **kwargs):
		if not await self.setting_enable_join_msg.get_value():
			return

		if player.flow.is_spectator:
			message = '$ff0{} $fff{}$z$s$ff0 joined the server as spectator! {}'
		else:
			message = '$ff0{} $fff{}$z$s$ff0 joined the server! {}'
		await self.instance.chat(
			message.format(
				player.get_level_string(), player.nickname,
				'Nation: $fff{}'.format(player.flow.zone.country) if player.flow.zone else ''
			)
		)

	async def player_disconnect(self, player, **kwargs):
		if not await self.setting_enable_leave_msg.get_value():
			return

		await self.instance.chat(
			'$ff0{} $fff{}$z$s$ff0 left the server! {}'.format(
				player.get_level_string(), player.nickname,
				'Nation: $fff{}'.format(player.flow.zone.country) if player.flow.zone else ''
			)
		)

