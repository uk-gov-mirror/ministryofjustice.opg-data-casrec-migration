from colorama import init, Back, Fore
from tabulate import tabulate


def format_details(details):
    report = ""
    try:
        for i in details["fail"]:
            row = Fore.RED + i + Fore.RESET + "\n"
            report += row
        if len(details["fail"]) == 0:
            row = Fore.GREEN + "n/a" + Fore.RESET + "\n"
            report += row
    except KeyError:
        row = Fore.GREEN + "n/a" + Fore.RESET + "\n"
        report += row

    return report


def format_report(list_of_tests):
    report = []
    for t in list_of_tests:
        if t["result"][0]:
            colour = Fore.GREEN
        else:
            colour = Fore.RED

        failure_details = format_details(details=t["result"][1])

        row = [
            t["name"],
            failure_details,
            colour + str(t["result"][0]) + Fore.RESET,
        ]
        report.append(row)
    return tabulate(
        report, headers=["test", "failure details", "success"], tablefmt="pretty"
    )
