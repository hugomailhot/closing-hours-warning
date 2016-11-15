# !/usr/bin/env python
# encoding: utf-8

"""
This script will scrape the Shields Library closing hours, then play a warning
message at regular intervals when the library is about to lock its door.

Past closing time, it will wait until 4am the next morning to scrape the next closing
hours.

This script relies on a commmand-line utility that will play an mp3 file.

For Windows, make sure that DLC media player can run with this command:
dlc -w <filename>

For Linux, use mpg321:
mpg321 <filename> -quiet

For OSX, use afplay:
afplay <filename>
"""

from datetime import datetime, timedelta
from lxml import html
import platform
import re
import requests
from time import sleep
from gtts import gTTS
import os


warning_msg_fp = 'warning.mp3'


def generate_warning_text(closing_time):
    if closing_time.hour == 0:
        closing_hour_str = 'midnight'
    elif closing_time.minute == 0 :
        closing_hour_str = closing_time.strftime('%I %p')
    else:
        closing_hour_str = closing_time.strftime('%I:%M %p')
    if 0 < closing_time.hour < 10 or 12 < closing_time.hour < 22:
        closing_hour_str = closing_hour_str[1:]  # Remove leading zero

    return ('Attention. Attention. The library will lock its doors '
            'at {}. '.format(closing_hour_str)) * 2  # Say it twice


def get_closing_time():
    # Extract opening hours string from library website
    closing_hours_page = requests.get('https://www.library.ucdavis.edu/ul/about/hours/')
    html_tree = html.fromstring(closing_hours_page.content)
    opening_hours_str = html_tree.xpath('//*[@id="hours"]/div[1]/div[1]/h4/text()')[0]
    
    # opening_hours_str looks like this: 
    # " Today - Friday November 4:   Open 7:30am-6:00pm"
    match = re.search(r'Today - (\w+ \w+ \d+):.+?-(\d+:\d+[ap]m)', opening_hours_str)
    closing_time_str = match.group(1) + ' ' + match.group(2)
    
    # Convert string to datetime object
    closing_time = datetime.strptime(closing_time_str, '%A %B %d %I:%M%p')
    # At this point closing_time.year == 1900. Now we fix this.
    closing_time = closing_time.replace(year=datetime.now().year)

    # Increment day if closing hour is midnight (it's zeroth hour of the next day)
    if closing_time.hour == 0:
        closing_time += timedelta(days=1)

    return closing_time


def play_mp3(mp3_file):
    pf_sys = platform.system()
    if pf_sys == 'Windows':
            os.system('dlc -w {}'.format(warning_msg_fp))
    elif pf_sys == 'Linux':
        os.system('mpg321 {}'.format(warning_msg_fp))
    elif pf_sys == 'Darwin':  # This is Mac OSX
        os.system('afplay {}'.format(warning_msg_fp))
    else:
        raise OSError("Your OS is not supported. Run this in Windows/OSX/Linux.")


sleep_until_4 = False
closing_time = None

while True:

    try:
        if sleep_until_4:
            if datetime.now().hour == 4:
                sleep_until_4 = False
                closing_time = None
            else:
                print("Sleeping until 4am")
                time.sleep(50*60)
                continue

        if closing_time == None:
            print("---------------------------------------------------------")
            print("Getting closing time")
            closing_time = get_closing_time()                    
            print("Closing time is {}".format(closing_time))
            warning_text = generate_warning_text(closing_time)
            warning_audio = gTTS(text=warning_text, lang='en')
            warning_audio.save(warning_msg_fp)  # This saves the warning as an mp3 file

        mins_before_close = (closing_time - datetime.now()).total_seconds() / 60.0
        print("Minutes before library closes: {}".format(mins_before_close))
        if 0 < mins_before_close < 15:
            print("{} mins left to leave. Playing warning message".format(mins_before_close))
            play_mp3(warning_msg_fp)

        elif mins_before_close < 0:
            print("Past closing time. Sleeping until 4am.")
            os.remove(warning_msg_fp)
            sleep_until_4 = True
        print("Too early to play warning. Sleeping for 5 mins.")
        sleep(5*60) 

    except Exception as e:
        # TODO: send email to admin so they can fix the problem
        raise e
        # Kill the program
        break
