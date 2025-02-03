import imaplib
import email
import os
import time
import configparser
import argparse
from imapclient import IMAPClient
from collections import defaultdict
from email.utils import getaddresses
from email.header import decode_header
from email import policy
from tqdm import tqdm
import subprocess

# Argument Parser for Manual Input Mode
parser = argparse.ArgumentParser(description="Email Backup Script")
parser.add_argument("--manual", action="store_true", help="Enable manual input mode instead of using config.ini")
args = parser.parse_args()

# Load configuration from config.ini or manual input
config = configparser.ConfigParser()

if args.manual:
    # Ask for user input
    IMAP_SERVER = input("Enter IMAP server (e.g., imap.gmail.com): ").strip()
    EMAIL_ACCOUNT = input("Enter your email address: ").strip()
    EMAIL_PASSWORD = input("Enter your email password (or app password): ").strip()
    START_DATE = input("Enter start date (DD-MMM-YYYY, leave empty for all): ").strip()
    END_DATE = input("Enter end date (DD-MMM-YYYY, leave empty for all): ").strip()
else:
    config.read("config.ini")
    IMAP_SERVER = config["IMAP"]["server"]
    EMAIL_ACCOUNT = config["IMAP"]["login"]
    EMAIL_PASSWORD = config["IMAP"]["password"]
    START_DATE = config["IMAP"].get("start_date", "").strip()
    END_DATE = config["IMAP"].get("end_date", "").strip()

# Define archive name based on current timestamp
ARCHIVE_NAME = f"backup_{time.strftime('%d%m%y%H%M%S')}"
SAVE_DIR = ARCHIVE_NAME  # Temporary folder for storing emails & attachments
ATTACHMENTS_DIR = os.path.join(SAVE_DIR, "attachments")
CONTACTS_FILE = os.path.join(SAVE_DIR, "contacts.txt")

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

contacts = defaultdict(set)
attachment_count = defaultdict(int)

def decode_mime_string(value):
    """Decodes MIME-encoded strings (e.g., =?utf-8?B?...?=)"""
    if not value:
        return value
    decoded_parts = decode_header(value)
    decoded_str = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            encoding = encoding or "utf-8"
            try:
                decoded_str += part.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                decoded_str += part.decode("utf-8", errors="ignore")
        else:
            decoded_str += part
    return decoded_str.strip()

def sanitize_filename(filename):
    """Formats filenames (removes invalid characters)"""
    return "".join(c if c.isalnum() or c in ('.', '_') else "_" for c in filename)

def extract_contacts(msg):
    """Extracts contacts from email headers"""
    headers = ["From", "To", "Cc", "Bcc"]
    for header in headers:
        if msg[header]:
            for name, email_addr in getaddresses([msg[header]]):
                if email_addr:
                    decoded_name = decode_mime_string(name)
                    contacts[email_addr.lower()].add(decoded_name if decoded_name else email_addr.lower())

def save_contacts():
    """Saves extracted contacts to a file with encoding fixes"""
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        for email_addr, names in contacts.items():
            for name in names:
                fixed_name = decode_mime_string(name)  # Ensure correct encoding
                f.write(f"{email_addr}:{fixed_name}\n")

    print(f"\n✅ Contacts saved to {CONTACTS_FILE}")

def connect_imap():
    """Connects to the IMAP server"""
    try:
        client = IMAPClient(IMAP_SERVER, port=993, use_uid=True, ssl=True)
        client.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        return client
    except imaplib.IMAP4.error as e:
        print(f"❌ Connection error: {e}")
        return None

def calculate_mailbox_size(client, messages):
    """Calculates the total size (in bytes) of all emails in a mailbox"""
    total_size = 0
    for msgid in messages:
        size_info = client.fetch([msgid], ["RFC822.SIZE"])
        total_size += size_info[msgid][b"RFC822.SIZE"]
    return total_size

def fetch_mailbox(client, mailbox):
    """Downloads emails and attachments from a specific mailbox"""
    print(f"\n📂 Processing mailbox: {mailbox}")

    try:
        client.select_folder(mailbox)

        search_criteria = ["ALL"]
        if START_DATE and END_DATE:
            search_criteria = [f"SINCE {START_DATE}", f"BEFORE {END_DATE}"]
        elif START_DATE:
            search_criteria = [f"SINCE {START_DATE}"]
        elif END_DATE:
            search_criteria = [f"BEFORE {END_DATE}"]

        messages = client.search(search_criteria)
        total_messages = len(messages)
        print(f"  🔍 Found {total_messages} emails in {mailbox}")

        if total_messages == 0:
            return

        total_size = calculate_mailbox_size(client, messages)
        downloaded_size = 0

        mailbox_dir = os.path.join(SAVE_DIR, mailbox.replace("/", "_"))
        os.makedirs(mailbox_dir, exist_ok=True)

        with tqdm(total=total_size, desc=f"  📩 {mailbox}", unit="B", unit_scale=True) as pbar:
            for msgid in messages:
                raw_message = client.fetch([msgid], ["RFC822"])[msgid][b"RFC822"]
                msg = email.message_from_bytes(raw_message, policy=policy.default)

                subject = decode_mime_string(msg["Subject"]) if msg["Subject"] else "No_Subject"
                subject = sanitize_filename(subject)[:50]

                date_tuple = email.utils.parsedate_tz(msg["Date"])
                if date_tuple:
                    timestamp = time.mktime(date_tuple[:9])
                    date_str = time.strftime("%d%m%y%H%M%S", time.localtime(timestamp))
                else:
                    date_str = "000000000000"

                msg_filename = os.path.join(mailbox_dir, f"{date_str}-{subject}.msg")
                with open(msg_filename, "wb") as f:
                    f.write(raw_message)

                downloaded_size += len(raw_message)
                pbar.update(len(raw_message))

                extract_contacts(msg)

        print(f"✅ {mailbox} processed successfully.")

    except Exception as e:
        print(f"  ❌ Error processing {mailbox}: {e}")

def fetch_all_emails():
    """Processes all mailboxes and downloads emails and attachments"""
    client = connect_imap()
    if not client:
        return

    mailboxes = [box[2] for box in client.list_folders()]
    for mailbox in mailboxes:
        fetch_mailbox(client, mailbox)

    client.logout()
    save_contacts()

def archive_emails():
    """Archives all downloaded emails and attachments into a .7z file"""
    print("\n📦 Archiving files...")
    archive_path = f"{ARCHIVE_NAME}.7z"
    cmd = ["7z", "a", "-mx9", archive_path, SAVE_DIR]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"\n✅ Archive created: {archive_path}")

if __name__ == "__main__":
    fetch_all_emails()
    archive_emails()
