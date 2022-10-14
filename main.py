from warnings import catch_warnings
import requests, staseraInTvScraper, cb01Scraper, webbrowser, os, _thread, time, sys
from http.server import HTTPServer, CGIHTTPRequestHandler

summaryPageName = 'freeTV.html'
urlsToScrape = {
    'staseraInTvURL': 'https://www.staseraintv.com',
    'cb01URL': 'https://cb01.builders'
}
numberOfPagesToAnalyze = 3 # first 3 pages

def createAndOpenSummaryFile(summaryPageName):
    strStyle = "<style>th, td {border: 1px solid black; border-radius: 10px; text-align:center; padding-left: 5px; padding-right: 5px;}</style>"
    strTable = "<html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'></head>" + strStyle + "<table>"
    file = open(summaryPageName, 'a', encoding="utf-8")
    file.write(strTable)
    return file

def closeSummaryFile(summaryPageFile):
    strTable = "</table></html>"
    summaryPageFile.write(strTable)
    summaryPageFile.close()

def start_server():    
    # Make sure the server is created at current directory
    os.chdir(os.getcwd())
    # Create server object listening the port 80
    server_object = HTTPServer(server_address=('127.0.0.1', 3600), RequestHandlerClass=CGIHTTPRequestHandler)
    # Start the web server
    server_object.serve_forever()

def isUrlReachable(url):
    try:
        requests.get(url)
        return True
    except Exception:
        return False

# START

# check reachability of URLs of each page to scrape
for url in urlsToScrape.keys():
    while not isUrlReachable(urlsToScrape[url]):
        print('l\'indirizzo %s' % (urlsToScrape[url]), 'potrebbe essere cambiato/errato, controllalo e reinserisci quello corretto: ') 
        urlsToScrape[url] = str(input())

# remove summary page file if It already exists
try:
    os.remove(summaryPageName)
except OSError:
    pass

_thread.start_new_thread(start_server,())

summaryPageFile = createAndOpenSummaryFile(summaryPageName)
staseraInTvScraper.start(summaryPageFile, urlsToScrape['staseraInTvURL'], numberOfPagesToAnalyze)
cb01Scraper.start(summaryPageFile, urlsToScrape['cb01URL'], numberOfPagesToAnalyze)
# add here other web site scraper
closeSummaryFile(summaryPageFile)

webbrowser.open('http://127.0.0.1:3600/' + summaryPageName)

# A thread continues to exist as long as the application continues to run, 
# in the case webbrowser.open_new() is not blocking so the browser 
# will hardly finish running the application, what you should do is make 
# a blocker to prevent the application finish of execute.
# So if the script finishes executing it will eliminate all its resources as the created threads.
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)