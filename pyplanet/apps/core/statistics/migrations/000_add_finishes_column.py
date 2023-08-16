from peewee import *
from playhouse.migrate import migrate, SchemaMigrator
from ..models import Score


def upgrade(migrator: SchemaMigrator):
	finishes = IntegerField(default=0)
	Score.truncate_table()
	migrate(
		migrator.add_column(Score._meta.db_table, 'finishes', finishes),
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Score._meta.db_table, 'finishes')
	)
