from pyplanet.contrib import CoreContrib
from pyplanet.contrib.chat.query import ChatQuery
from pyplanet.core.events import Signal
import asyncio


class ChatManager(CoreContrib):
	"""
	The Chat manager is available with: ``instance.chat`` shortcut.
	"""

	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.

		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.controller_chat = Signal(code="chat", namespace="pyplanet")
		self.instance.signals.register_signal(signal=self.controller_chat)

	def __call__(self, *args, **kwargs):
		if len(args) <= 0:
			return
		query = self.prepare(args[0], raw=kwargs.get('raw', False))

		if len(args) > 1:
			query.to_players(args[1:])

		asyncio.ensure_future(
			self.controller_chat.send(dict(text=query.get_formatted_message(), logins=query.get_recipients()), True)
		)

		return query

	def prepare(self, message=None, raw=False):
		"""
		Prepare a Chat Query by returning a Chat Query object.

		:param message: Messsage predefined or build later.
		:param raw: Don't append prefixes or add any automatic message parts.
		:return: Query instance
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""

		return ChatQuery(self, message, auto_prefix=not raw)

	def prepare_raw(self, message=None):
		"""
		Prepare raw message query without prefixes!

		:param message: Predefined message.
		:return: Query instance
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""
		return self.prepare(message, True)

	async def execute(self, *queries):  # pragma: no cover
		"""
		Execute and send one or multiple chat messages (prepared queries or raw strings) with a multicall.

		:param queries: One or more query instances or one or multiple strings that gets send as global messages.
		:return: The results of the multicall.
		"""
		for query in queries:
			if isinstance(query, ChatQuery):
				out = query.get_formatted_message()
				logins = query.get_recipients()
			else:
				message = self.prepare_raw(str(query))
				out = message.get_formatted_message()
				logins = message.get_recipients()

			await self.controller_chat.send(dict(text=out, logins=logins), True)

		return await self.instance.gbx.multicall(
			*[
				q.gbx_query if isinstance(q, ChatQuery)
				else self.prepare_raw(str(q)).gbx_query

				for q in queries
			]
		)
