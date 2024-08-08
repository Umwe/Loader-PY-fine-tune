import pyodbc

# Define the connection string using Windows Authentication
conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=UMWE-KUMUBUMBE\UMWE;'  # Replace with your server name
    r'DATABASE=testdb;'
    r'Trusted_Connection=yes;'
)

# Connect to the SQL Server
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Define the parameters for the stored procedure
file_name = 'PGW-NYREPG01_20240802111104_16399_PC.txt'
file_path = r'C:\Users\User\Downloads\test\PGW-NYREPG01_20240802111104_16399_PC.txt'

# Prepare the SQL command to execute the stored procedure
sql = """
DECLARE @ErrorMsg NVARCHAR(4000);

EXEC [dbo].[Load_GGSN_CDR_UNIX]
    @FileName = ?,
    @FilePath = ?,
    @ErrorMsg = @ErrorMsg OUTPUT;

SELECT @ErrorMsg AS ErrorMsg;
"""

try:
    # Execute the SQL command
    cursor.execute(sql, file_name, file_path)
    
    # Initialize the variable to store the output message
    error_msg = None

    # Fetch all result sets and handle messages
    while True:
        # Check if there is a description of the current result set
        if cursor.description:
            # Fetch the row
            row = cursor.fetchone()
            if row:
                # Check if the result set contains the error message
                if 'ErrorMsg' in cursor.description[0][0]:
                    error_msg = row.ErrorMsg
        # Move to the next result set
        if not cursor.nextset():
            break

    # Commit the transaction to ensure data is saved
    conn.commit()

    # Print the error message if available and determine the status
    if error_msg:
        status_code = error_msg[0]
        print(f"Error Message: {error_msg}")
        if status_code == '0':
            print("File loaded successfully.")
        elif status_code == '1':
            print("File already exists.")
        elif status_code == '-':
            print("File is corrupt or another error occurred.")
        else:
            print("Unknown status code.")
    else:
        print("No error message returned.")

except pyodbc.Error as e:
    print(f"Error occurred: {e}")
    conn.rollback()

finally:
    # Close the connection
    cursor.close()
    conn.close()
