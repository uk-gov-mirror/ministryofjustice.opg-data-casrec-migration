from pytest_cases import case


@case(id="current_date called")
def case_current_date():
    test_calculation = {
        "current_date": [
            {"original_col": ["this_is_a_date"], "final_col": "todays_date",}
        ],
    }

    log_message = "mock current_date"

    return (test_calculation, log_message)
