from pytest_cases import case


@case(id="current_date called")
def case_current_date():
    test_calculation = {
        "current_date": [{"column_name": "todays_date",}],
    }

    log_message = "mock current_date"

    return (test_calculation, log_message)
