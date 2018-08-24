from pyplanet.views.generics.widget import WidgetView
import json




class RoundPoints(WidgetView):
	widget_x = -120
	widget_y = 30
	template_name = 'widget_roundpoints/widget.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_roundpoints'

	async def get_context_data(self):
		points = await self.app.instance.gbx("Trackmania.GetPointsRepartition")
		context = await super().get_context_data()
		context.update({
			'points': json.dumps(points['pointsrepartition']),
		})

		return context
