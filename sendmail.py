#!/usr/bin/env python3

from simplegmail import Gmail
import argparse
import bs4

def sendMail(sender, to, subject, msgHtml, msgPlain, attachments, useSignature):

    gmail = Gmail() 
    params = {
        "sender": sender,
        "to": to,
        "subject": subject,
        "msg_html": msgHtml,
        "msg_plain": msgPlain,
        "attachments": attachments,
        "signature": useSignature
    }
    try:
       message = gmail.send_message(**params)
    except bs4.FeatureNotFound:
       pass # On Python 3.7, bs4 0.0.1, lxml does not work on some platforms, ignore
    except Exception as e:
       raise e


def getArgs():
    parser = argparse.ArgumentParser(description='SendMail via Gmail')
    parser.add_argument('sender', help="Sender's email")
    parser.add_argument('to', help="Recipient's email")
    parser.add_argument('subject', help="Subject line")
    parser.add_argument('-hm', help="Html message in file (path)")
    parser.add_argument('-pm', help="Plain message in file (path)")
    parser.add_argument('-a', action="append", nargs="?", help="Add an attachment, can have many -a")    
    parser.add_argument('-s', default=False, action='store_true', help="Use signature?")

    args = parser.parse_args()
    if not (args.hm or args.pm):
       parser.error('Need at least one: -hm (HTML message) or -pm (Plain message)')

    return args

def getMsgContentFromFile(filename):
    msg = None
    if filename != None:
        with open(filename, 'r') as f:
            msg = f.read()
    return msg


def sendMailCmdline(args):    
    htmlMsg = getMsgContentFromFile(args.hm)
    plainMsg = getMsgContentFromFile(args.pm)
    sendMail(args.sender, args.to, args.subject, htmlMsg, plainMsg, args.a, args.s)

if __name__ == "__main__":
    args = getArgs()
    sendMailCmdline(args)    
