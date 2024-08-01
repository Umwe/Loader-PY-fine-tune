import pyodbc

def connect_to_db(server, database, auth_type, username=None, password=None):
    if auth_type == "Windows Authentication":
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    return pyodbc.connect(connection_string)

def call_stored_procedure(connection, stored_procedure, file_name, file_path):
    cursor = connection.cursor()
    error_msg = ""
    try:
        cursor.execute(f"EXEC {stored_procedure} @FileName=?, @FilePath=?, @ErrorMsg=?", (file_name, file_path, error_msg))
        connection.commit()
        error_msg = cursor.getvalue("@ErrorMsg")
        status = int(error_msg[0])
        message = error_msg[1:]
        return status, message
    except Exception as e:
        print(f"Error calling stored procedure: {e}")
        return -1, str(e)
