from helpers import *


def target_update(config, conn_migration, conn_target):
    # print("- Cases")
    # sql = "SELECT *" "FROM etl3.cases " "WHERE sirius_id IS NOT NULL "
    # cases_df = pd.read_sql_query(sql, con=migration_db_engine, index_col=None)
    # cases_df = cases_df.drop(["id", "c_order_no"], axis=1)
    # cases_df = cases_df.rename(columns={"sirius_id": "id"})
    # cases_df = cases_df.rename(columns={"sirius_client_id": "client_id"})
    # cases_df = cases_df.rename(columns={"ordersubtype": "casesubtype"})
    # cases_df["casetype"] = cases_df["type"].str.upper()
    # print(cases_df)
    # cases_df.to_sql(
    #     "cases_migrated",
    #     sirius_db_engine,
    #     if_exists="replace",
    #     index=False,
    #     chunksize=500,
    #     dtype={
    #         "id": Integer(),
    #         "client_id": Integer(),
    #         "uid": BigInteger,
    #         "type": String(255),
    #         "casetype": String(255),
    #         "casesubtype": String(255),
    #         "caserecnumber": String(255),
    #         "orderdate": Date,
    #         "orderissuedate": Date,
    #         "orderexpirydate": Date,
    #         "statusdate": Date,
    #     },
    # )


def target_add(config, conn_migration, conn_target):
    # print("- Cases")
    # # needs an index
    # sql = """UPDATE etl3.cases
    #         SET sirius_client_id = map.id
    #         FROM etl3.sirius_map_persons map
    #         WHERE map.caserecnumber = cases.caserecnumber"""
    # migration_db_engine.execute(sql)
    #
    # sql = (
    #     "SELECT *"
    #     "FROM etl3.cases "
    #     "WHERE sirius_id IS NULL "
    #     "AND orderdate IS NOT NULL "
    #     "AND orderissuedate IS NOT NULL "
    #     "AND orderexpirydate IS NOT NULL "
    #     "AND statusdate IS NOT NULL "
    #     "AND orderdate != '' "
    #     "AND orderissuedate != '' "
    #     "AND orderexpirydate != '' "
    #     "AND statusdate != '' "
    # )  # There are nulls in the data for dates, but the DB is not null. Something's screwy somewhere
    # # but for now, just select data with no nulls
    # cases_df = pd.read_sql_query(sql, con=migration_db_engine, index_col=None)
    # cases_df = cases_df.drop(["id", "sirius_id", "c_order_no"], axis=1)
    # cases_df = cases_df.rename(columns={"sirius_client_id": "client_id"})
    # cases_df = cases_df.rename(columns={"ordersubtype": "casesubtype"})
    # cases_df["casetype"] = cases_df["type"].str.upper()
    # cases_df.to_sql(
    #     "cases",
    #     sirius_db_engine,
    #     if_exists="append",
    #     index=False,
    #     chunksize=500,
    #     dtype={
    #         "client_id": Integer,
    #         "uid": BigInteger,
    #         "type": String(255),
    #         "casetype": String(255),
    #         "casesubtype": String(255),
    #         "caserecnumber": String(255),
    #         "orderdate": Date,
    #         "orderissuedate": Date,
    #         "orderexpirydate": Date,
    #         "statusdate": Date,
    #     },
    # )
