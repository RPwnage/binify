import requests, argparse

# from rich import print
from MailTMClient import MailTMClient
import sys, pickle, json

TOKEN_FILE = "token.json"


def saveTokenToFile(token: str):
    with open(TOKEN_FILE, "r+") as j:
        contents = json.loads(j.read())
        contents["token"] = token
        j.seek(0)
        j.write(json.dumps(contents, indent=4))
        j.truncate()


def loadTokenFromFile():
    with open(TOKEN_FILE, "r+") as j:
        contents = json.loads(j.read())
        if len(contents["token"]) > 10:
            return contents["token"]
        else:
            return False


def clearTokenFile():
    with open(TOKEN_FILE, "w") as j:
        j.write(json.dumps({"token": ""}, indent=4))


TOKEN = loadTokenFromFile()

parser = argparse.ArgumentParser(
    description="A terminal based client for quick access to MailTM"
)

if TOKEN == False:
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-r",
        "--register",
        help="Create a new Account, with given address and password",
        action="store_true",
    )

    group.add_argument(
        "-l",
        "--login",
        help="Login to an existing Account",
        action="store_true",
    )

    parser.add_argument(
        "-a",
        "--address",
        help="address to login to an existing Account",
        type=str,
        required=("--login" in sys.argv or "--register" in sys.argv),
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password to login to an existing Account",
        type=str,
        required=("--login" in sys.argv or "--register" in sys.argv),
    )

    parser.add_argument(
        "--domains",
        help="Obtain a list of currently available domains.",
        required=False,
        action="store_true",
    )
else:
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-i",
        "--inbox",
        help="Obtain a list of emails in your inbox.",
        required=False,
        action="store_true",
    )

    group.add_argument(
        "-l",
        "--logout",
        help="Logout of an existing Account",
        required=False,
        action="store_true",
    )

    group.add_argument(
        "-r",
        "--readmail",
        help="Read an email from your inbox, using the ID you can see with --inbox",
        type=int,
        required=False,
    )

    group.add_argument(
        "-d",
        "--deletemail",
        help="Delete an email from your inbox, using the ID you can see with --inbox",
        type=int,
        required=False,
    )

args = parser.parse_args()
if TOKEN:
    client = MailTMClient(token=TOKEN)
    if args.inbox == True:
        inbox = (client.getInbox())[::-1]
        if len(inbox) >= 1:
            for index, email in enumerate(inbox):
                print(
                    "[" + str(index + 1) + "]",
                    email.subject,
                    "(Sender: " + email.fromAddress + ")",
                )
        else:
            print("[i] Your inbox is currently empty!")
    if args.readmail:
        inbox = client.getInbox()
        for index, email in enumerate(inbox):
            if int(index + 1) == int(args.readmail):
                print("[i] Subject: " + email.subject)
                print("[i] Sender: " + email.fromAddress)
                print("[i] Recipients: " + ", ".join(email.toAddress))
                print("[i] Content:\n" + email.text)
                exit()
        print("[!] We did not find an email with that ID!")
    if args.deletemail:
        inbox = client.getInbox()
        for index, email in enumerate(inbox):
            if int(index + 1) == int(args.deletemail):
                res = email.delete()
                if res == 0:
                    print("[i] Successfully deleted the email!")
                if res == 1:
                    print("[i] Could not found the email!")
                exit()
        print("[i] Could not found the email!")
    if args.logout == True:
        clearTokenFile()
        print("[i] Successfully logged out of your MailTM Account.")
if TOKEN == False:
    if args.domains == True:
        domains = MailTMClient().getAvailableDomains()
        for index, domain in enumerate(domains):
            print("[" + str(index + 1) + "]", domain.domain)
    if args.register == True:
        (responseCode, response) = MailTMClient().register(args.address, args.password)
        if responseCode == 0:
            print("[i] Successfully created an MailTM Account!")
            saveTokenToFile(response)
        if responseCode != 0:
            print("[!] Failed to create an MailTM Account! (" + str(response) + ")")
    if args.login == True:
        (responseCode, response) = MailTMClient().login(args.address, args.password)
        if responseCode == 0:
            print("[i] Successfully logged into an MailTM Account!")
            saveTokenToFile(response)
        if responseCode == 1:
            print("[!] Failed to log into an MailTM Account! (" + str(response) + ")")
