import asynctest

from pyplanet.core import Controller


class ControllerTestCase(asynctest.TestCase):

	async def setUp(self):
		self.instance = Controller.prepare(name='default').instance
		await self.instance._start()

	async def tearDown(self):
		await self.instance.gbx.disconnect()
		try:
			await self.instance.db.engine.disconnect()
		except:
			pass
		del self.instance
