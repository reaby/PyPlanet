import math

from pyplanet.views.generics.widget import TimesWidgetView


class CPWidgetView(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	size_x = 38
	size_y = 55.5
	title = 'Current CPs'

	template_name = 'currentcps2/cpwidget.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_currentcps'

		self.record_amount = 15

	async def get_context_data(self):
		context = await super().get_context_data()

		# Add facts.
		context.update({
			'records_amount': self.record_amount
		})

		return context
