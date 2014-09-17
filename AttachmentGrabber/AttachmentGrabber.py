import email
import getpass
import imaplib
import os
import time

def grab_attachments(user, server, folder, out_dir):
# Downloads all attachments from "folder" in account "user" on "server".
# Places in directories in "out_dir" named by sender emails.

    m = imaplib.IMAP4_SSL(server)

    print("Attempting to log in to {0:s} on {0:s}...".format(user, server))
    passwd = getpass.getpass("Password: ")
    type, details = m.login(user, passwd)
    if type != 'OK':
        print("UNSUCCESSFUL")
        raise
    del passwd
    print("SUCCESSFUL")

    type, details = m.select(folder)
    if type != 'OK':
        print("FOLDER NOT FOUND")
        raise

    type, data = m.search(None, 'ALL')
    if type != 'OK':
        print("SEARCH ERROR")
        raise

    files = []
    dates = []

    for id in data[0].split():
        type, msgparts = m.fetch(id, '(RFC822)')
        if type != 'OK':
            print("FETCH ERROR")
            raise

        body = msgparts[0][1]
        mail = email.message_from_string(body)
        headers = email.parser.HeaderParser().parsestr(body)
        name, addr = email.utils.parseaddr(headers['From'])
        date = email.utils.parsedate(headers['Date'])

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()

            if bool(fileName):
                dir = os.path.join(out_dir, addr.split('@')[0])
                if not os.path.isdir(dir):
                    os.system("mkdir -p " + dir)

                filePath = os.path.join(dir, fileName)
                if filePath not in files:
                    print(addr + ": " + fileName)
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    files.append(filePath)
                    dates.append(date)
                else:
                    i = files.index(filePath)
                    if time.mktime(date) > time.mktime(dates[i]):
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        dates[i] = date

    output = []
    for i,f in enumerate(files):
        output.append((f, dates[i]))

    #Clean up
    m.close()
    m.logout()

    return output

