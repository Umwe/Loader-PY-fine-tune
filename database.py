import pyodbc

def connect_to_db(server, database, auth_type, username=None, password=None):
    if auth_type == "Windows Authentication":
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    return pyodbc.connect(connection_string)

def call_stored_procedure(connection, stored_procedure, file_path):
    cursor = connection.cursor()
    try:
        cursor.execute(f"EXEC {stored_procedure} ?", file_path)
        connection.commit()
        result = cursor.fetchone()
        status = result[0]  # Assuming the stored procedure returns status as the first column
        message = result[1]  # Assuming the stored procedure returns message as the second column
        return status, message
    except Exception as e:
        return -1, str(e)
