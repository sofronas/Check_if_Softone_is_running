import psutil
import platform
import uuid
import socket
import urllib.request
import smtplib
import ssl
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def getMacAdress():
    print("MAC Address: \t\t\t", end="")
    print(':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
    for ele in range(0, 8 * 6, 8)][::-1]))
    macaddr = uuid.getnode()
    macaddr = ':'.join(("%012X" % macaddr)[i: i + 2] for i in range(0, 12, 2))
    return macaddr

def getLocalIp():
    print("Local IP: \t\t\t", socket.gethostbyname(socket.gethostname()))
    return socket.gethostbyname(socket.gethostname())

def sentEmailToKostas(out_ip, platform, uname, mac_address, local_ip, available_networks):
    now = datetime.datetime.now()
    d = now.strftime("%d_%m_%Y")
    subject = "Softone " + "- " + d + " - Running"
    networks = ','.join(str(e) for e in available_networks)
    body = "Softone Running:\n**********************************\n" + "External IP: \t\t" + out_ip + \
    "\nPlatform:    \t\t" + platform + "\nUsername: \t\t" + uname + "\nMAC Address: \t\t" + mac_address + \
    "\nLocal IP: \t\t" + local_ip + "\nNetwork Adapter: \t\t" + networks + "\n**********************************\n"
    sender_email = "sender@mail.gr"
    receiver_email = "receiver@0mail.gr"
    password = "password"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("mail.mail.gr", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

softone_name = "xplorer.exe" # Softone running process name
local_ip = "127.0.0.1"
out_ip = "127.0.0.1"
mac_adress = "xx:xx:xx:xx:xx:xx"
email_send = False
while True:
    if softone_name in (p.name() for p in psutil.process_iter()):
        if not email_send:
            print("Softone Running")
            print("**********************************")
            out_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
            print('External IP: \t\t', out_ip)
            print("Platform:    \t\t", platform.platform())
            print("Username:    \t\t", platform.uname().node)
            mac_address = getMacAdress()
            local_ip = getLocalIp()
            addresses = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            available_networks = []
            for intface, addr_list in addresses.items():
                if any(getattr(addr, 'address').startswith("169.254") for addr in addr_list):
                    continue
                elif intface in stats and getattr(stats[intface], "isup"):
                    available_networks.append(intface)

            print("Network Adapter: \t\t", available_networks)
            print("**********************************")
            # send email
            email_send = True
            sentEmailToKostas(out_ip,platform.platform(),platform.uname().node,mac_address,local_ip,available_networks)
    else:
        email_send = False
        print("Softone is not running")
