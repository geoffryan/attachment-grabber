import email
import getpass
import imaplib
import os

def grab_attachments():

    m = imaplib.IMAP4_SSL("imap.gmail.com")
    
    user = raw_input("GMail username (or address): ")
    passwd = getpass.getpass("Password: ")



