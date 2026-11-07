"""The data every environment needs, production too.

Each module has async seed_ functions that take the session. They run
in the order of the module and the function names, after the
migrations and in their transaction, on each deployment: a seeder
writes what is missing and never duplicates a row.
"""
