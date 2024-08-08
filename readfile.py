with open('C:\Users\User\Downloads\tem\PGW-NYREPG01_20240802111104_16399', 'rb') as file:
    content = file.read()
    if b'\r\n' in content:
        print("The file uses Windows-style line endings (CRLF).")
    elif b'\n' in content:
        print("The file uses Unix-style line endings (LF).")
    elif b'\r' in content:
        print("The file uses old Mac-style line endings (CR).")
    else:
        print("Unknown or mixed line endings.")
