import sys
import os
from functools import reduce

environment = os.environ.get("ENVIRONMENT")

if environment == "local":

    # allow imports when running script from within project dir
    [sys.path.append(i) for i in [".", ".."]]

    # allow imports when running script from project dir parent dirs
    list_of_things = []
    script_path = os.path.split(sys.argv[0])
    for i in range(len(script_path)):
        sys.path.append(reduce(os.path.join, script_path[: i + 1]))

    print("I am importing things from the high level shared directory")
    from migration_steps import shared_utilities as shared


else:
    print("I am importing things from the shared directory inside the app folder")
    import shared_utilities as shared
