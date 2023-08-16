"""
Trackmania app component.
"""
from pyplanet.apps.core.statistics.models import Score
from pyplanet.apps.core.statistics.views.dashboard import StatsDashboardView
from pyplanet.apps.core.statistics.views.records import TopSumsView
from pyplanet.apps.core.statistics.views.score import StatsScoresListView, CheckpointComparisonView
from pyplanet.apps.core.trackmania.callbacks import finish, give_up
from pyplanet.contrib.command import Command
from pyplanet.apps.core.maniaplanet.models import Player


class TrackmaniaComponent:

	def __init__(self, app):
		"""
		Initiate trackmania statistics component.

		:param app: App config instance
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		self.app = app

	async def on_init(self):
		pass

	async def get_without_failing(self, player):
		curr = self.app.instance.map_manager.current_map.get_id()
		results = await Score.execute(Score.select().where((Score.player == player.get_id()) & (Score.map == curr)).limit(1))
		return results[0] if len(results) > 0 else None

	async def on_start(self):
		# Listen to signals.
		self.app.context.signals.listen(finish, self.on_finish)

		# Register commands.
		await self.app.instance.command_manager.register(
			# Command('stats', target=self.open_stats),
			Command('topsums', target=self.topsums, description='Displays a list of top record players.'),
			Command(command='scoreprogression', aliases=['progression'], target=self.open_score_progression,
					description='Displays your time/score progression on the current map.'),
			Command(command='cpcomparison', aliases=['cp'], target=self.open_cp_comparison,
					description='Compares your checkpoints times with the local record and the ideal checkpoints.'),
		)

	async def on_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		# Register the score of the player.
		if isinstance(player, Player):
			obj = await self.get_without_failing(player)
			if obj is not None:
				obj.finishes = int(obj.finishes + 1)
				if obj.score and int(race_time) < obj.score:
					obj.score = int(race_time)
					obj.checkpoints = str(','.join([str(cp) for cp in cps]))
				await obj.save()
			else:
				await Score(
					player=player,
					map=self.app.instance.map_manager.current_map,
					score=race_time,
					checkpoints=','.join([str(cp) for cp in cps]),
					finishes=1
				).save()

	async def open_stats(self, player, **kwargs):
		view = StatsDashboardView(self.app, self.app.context.ui, player)
		await view.display()

	async def open_score_progression(self, player, **kwargs):
		view = StatsScoresListView(self.app, player)
		await view.display(player)

	async def open_cp_comparison(self, player, **kwargs):
		view = CheckpointComparisonView(self.app, player)
		await view.display(player)

	async def topsums(self, player, *args, **kwargs):
		await self.app.instance.chat('$0f3Loading Top Record Players ...', player)
		view = TopSumsView(self.app, player, await self.app.processor.get_topsums())
		await view.display(player)
