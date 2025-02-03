# emaildumper

Email Backup Script

This Python script downloads all emails and attachments from an IMAP server, saves them locally, extracts contacts, and archives everything in `.7z` format.

List Of Dependencies
| Library         | Purpose |
|---------------------|------------|
| imapclient      | Connects to IMAP and fetches emails. |
| email-validator | Validates email addresses. |
| requests        | May be useful for network requests (optional). |
| tqdm           | Displays progress bars while downloading emails. |
| p7zip-full     | Utility for `.7z` archive creation (needed on Linux). |

📦 Installation

1. Clone the repository
```sh
git clone https://github.com/axshaman/emaildumper.git
cd emaildumper
```

AUTO INSTALL

📌 How to Use the Auto-Installer
Run the script for installation:
   ```sh
   chmod +x install.sh
   ./install.sh
   ```

Run the script for using later:
   ```sh
   source myenv/bin/activate
   python fetch_and_archive.py
   ```

MANUAL INSTALL

2. Setting up a Virtual Environment
```sh
python -m venv myenv
source myenv/bin/activate  # Linux/macOS
myenv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install --user tqdm
```

3. Installing Additional Dependencies (if required)
```sh
sudo apt update
sudo apt install p7zip-full -y
```
4. Editing `config.ini`
The `config.ini` file stores IMAP server details and the email retrieval period.

- If both `start_date` and `end_date` are empty, it fetches all emails.  
- If only one date is provided, it fetches emails up to or from that date.  

#Example `config.ini`
```
[IMAP]
server = imap.gmail.com
login = your_email@gmail.com
password = your_password
start_date = 01-Jan-2024
end_date = 02-Feb-2024
```

5. Running the Script
#Using `config.ini` settings
```sh
python fetch_and_archive.py
```

#Manually entering IMAP settings
If `--manual` is passed, the script will prompt the user to enter server, login, password, and date range manually.
```sh
python fetch_and_archive.py --manual
```

6. Output Files
After execution, the following files will be created:
- Downloaded emails folder: `backup_010224120000/`
- Extracted contacts file: `contacts.txt`
- Compressed archive: `backup_010224120000.7z`