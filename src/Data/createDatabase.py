import duckdb

def createDatabase(path):
    connection = duckdb.connect(path)
    return connection
