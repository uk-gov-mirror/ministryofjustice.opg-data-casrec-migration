from helpers import *


def load_fixtures(self, conn_migration, conn_target):
    # print("- Associated cases")
    # sql = "SELECT id, caserecnumber FROM persons ORDER BY id DESC LIMIT 10"
    # persons_fixtures = pd.read_sql_query(sql, con=sirius_db_engine, index_col=None)
    #
    # sql = """
    # SELECT *
    # FROM etl3.cases
    # WHERE caserecnumber
    # IN (SELECT caserecnumber FROM etl3.persons ORDER BY id ASC LIMIT 5)
    # """
    # etl_cases_df = pd.read_sql_query(sql, con=migration_db_engine, index_col=None)
    #
    # cases_df = etl_cases_df.merge(
    #     persons_fixtures,
    #     how="left",
    #     left_on="caserecnumber",
    #     right_on="caserecnumber",
    #     suffixes=["_case", "_person"],
    # )
    #
    # print(etl_cases_df)
    #
    # cases_df = cases_df.drop(
    #     ["id_case", "c_order_no", "sirius_id", "sirius_client_id"], axis=1
    # )
    # cases_df = cases_df.rename(columns={"id_person": "client_id"})
    # cases_df = cases_df.rename(columns={"ordersubtype": "casesubtype"})
    # cases_df["casetype"] = cases_df["type"].str.upper()
    # print(cases_df)
    #
    # cases_df.to_sql(
    #     "cases",
    #     sirius_db_engine,
    #     if_exists="append",
    #     index=False,
    #     dtype={
    #         "orderdate": Date,
    #         "orderissuedate": Date,
    #         "orderexpirydate": Date,
    #         "statusdate": Date,
    #         "caserecnumber": String(255),
    #         "ordersubtype": String(255),
    #         "uid": BigInteger,
    #         "casetype": String(255),
    #         "client_id": Integer,
    #     },
    # )

    # sql = """
    # SELECT client_id, id
    # FROM cases WHERE caserecnumber IN
    # (SELECT caserecnumber FROM persons ORDER BY id DESC LIMIT 5)
    # """
    # person_caseitems_df = etl_cases_df = pd.read_sql_query(
    #     sql, con=sirius_db_engine, index_col=None
    # )
    # person_caseitems_df = person_caseitems_df.rename(columns={"client_id": "person_id"})
    # person_caseitems_df = person_caseitems_df.rename(columns={"id": "caseitem_id"})
    # person_caseitems_df.to_sql(
    #     "person_caseitem",
    #     sirius_db_engine,
    #     if_exists="append",
    #     index=False,
    #     dtype={"person_id": Integer, "case_id": Integer},
    # )
