from helpers import *


def load_fixtures(self, conn_target):
    print("- Associated addresses")
    execute_sql_file('fixtures_add_addresses.sql', conn_target)
