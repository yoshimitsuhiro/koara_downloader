## koara_downloader

This is a python script for downloading books automatically from Keio University's digital collection Koara.

This script will download all pages of a selected book in the highest quality jpgs available.

Please note that sending too many requests to the library's server at once will both slow the server down and get your IP blocked temporarily. For this reason, I have added a timer to wait between downloads. Please be considerate and do not set the time interval too low.

The following libraries are required to use this script: [bs4] (https://www.crummy.com/software/BeautifulSoup/), [Pillow] (https://pillow.readthedocs.io/en/3.3.x/), [requests] (http://docs.python-requests.org/en/master/), and [regex] (https://bitbucket.org/mrabarnett/mrab-regex).

When using this script in Windows, depending on your system locale, you may experience encoding errors in command prompt. This is a Windows problem and there is nothing that can be done to fix it in the code. To work around this issue, try changing the code table of command prompt to Unicode by using the following command: `chcp 65001`.
