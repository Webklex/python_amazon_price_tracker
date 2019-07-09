"""
* File: main.py
* Author: M.Goldenbaum
* Created: 09.07.19 23:40
* Updated: -
*
* Description:
* A simple Amazon price alert tracker
*
* Installation:
* pip install requests bs4
*
* Usage:
* python main.py
"""

import requests
from bs4 import BeautifulSoup
import smtplib
import time
from time import gmtime, strftime

"""
Default headers copied from a browser with german language settings. 
You might want to change these to your own..
"""
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu "
                  "Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36 ",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,"
              "*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "upgrade-insecure-requests": "1",
}

"""
Define your tracking tasks below.
:var email  string      The email address which will receive the alerts
:var url    string      The complete amazon product url
:var alert  float       Define a value where you want to be notified
"""
tasks = [
    {
        'email': 'someone@example.com',
        'url': 'https://www.amazon.de/Samsung-MZ-76PE512BW-interne-Zoll-schwarz/dp/B078WQL6XF/',
        'alert': 79.99
    }
]

"""
Enter your own SMTP mail settings below
"""
mail_config = {
    'host': "mx.example.com",
    'port': 587,
    'username': "sender@example.com",
    'password': "PASSWORD",
}

"""
If you want to check the price more often (might result in an ip ban / block) feel free to decrease or increase the
delay below. The default 300 represents 300 seconds aka 5 minutes.
"""
delay = 10


def check_price(key, url, alert, email):
    """
    Check the current price for a given url and report if the price alert is hit
    :var key    integer
    :var url    string
    :var alert  float
    :var email  string
    """

    try:
        page = requests.get(url, headers=headers)

        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find(id="productTitle").get_text().strip()
        price = soup.find(id="priceblock_ourprice").get_text().strip()

        c_price = float(price[0:len(price) - 2].strip().replace(",", "."))
        delta = c_price - alert

        print(f"Title: {title}")
        print(f"Current price: {price}")
        print(f"Target price: {alert}")
        print(f"Delta: {delta}")

    except:
        print(f"Failed to fetch: {url}")
        return

    if 'informed' not in tasks[key]:
        if c_price < alert:
            send_mail(email, title, c_price, url)
            tasks[key]['informed'] = True


def send_mail(to_addrs, title, price, url):
    """
    Send a price alert mail with all relevant information to a given mail address
    :var to_addrs   string
    :var title      string
    :var price      float
    :var url        string
    """

    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    subject = f"Price alert: {title}"
    body = f"Current price: {price}\n\nProduct page: {url}\n\nDatetime: {date}"

    msg = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP(host=mail_config['host'], port=mail_config['port'])
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user=mail_config['username'], password=mail_config['password'])
        server.sendmail(from_addr=mail_config['username'], to_addrs=to_addrs, msg=msg)
        server.quit()

        print("Message sent")
    except:
        print(f"Failed to send message to: {to_addrs}")
        return


if __name__ == '__main__':
    """
    Run forever in order to track the products as precise as possible
    """
    print("Amazon tracker started")

    while True:

        for i, task in enumerate(tasks):
            print("-----------------------------")
            check_price(i, task['url'], task['alert'], task['email'])

        time.sleep(delay)
