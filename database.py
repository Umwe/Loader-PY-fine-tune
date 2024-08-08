import pyodbc

def connect_to_db(server, database, auth_type, username=None, password=None):
    if auth_type == "Windows Authentication":
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    return pyodbc.connect(connection_string)

def call_stored_procedure(connection, stored_procedure, file_name, file_path):
    cursor = connection.cursor()
    sql = f"""
    DECLARE @ErrorMsg NVARCHAR(4000);

    EXEC {stored_procedure}
        @FileName = ?,
        @FilePath = ?,
        @ErrorMsg = @ErrorMsg OUTPUT;

    SELECT @ErrorMsg AS ErrorMsg;
    """

    try:
        cursor.execute(sql, file_name, file_path)
        error_msg = None

        while True:
            if cursor.description:
                row = cursor.fetchone()
                if row:
                    if 'ErrorMsg' in cursor.description[0][0]:
                        error_msg = row.ErrorMsg
            if not cursor.nextset():
                break

        connection.commit()

        if error_msg:
            return parse_error_msg(error_msg)
        else:
            return -1, 'No error message returned.'

    except pyodbc.Error as e:
        return -1, str(e)

    finally:
        cursor.close()

def parse_error_msg(error_msg):
    if error_msg.startswith('0'):
        return 0, error_msg
    elif error_msg.startswith('1'):
        return 1, error_msg
    elif error_msg.startswith('-'):
        return -1, error_msg
    else:
        return -1, 'Unknown error'
