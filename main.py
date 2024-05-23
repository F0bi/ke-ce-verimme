from warnings import catch_warnings
import requests, scrapers.staseraInTvScraper as staseraInTvScraper, scrapers.cb01Scraper as cb01Scraper, scrapers.justwatchScraper as justwatchScraper, webbrowser, os, _thread, time, sys
from http.server import HTTPServer, CGIHTTPRequestHandler
from sys import platform

summaryPageName = 'index.html'
scrapersSetting = {
    'staseraInTv': {
        'url': 'https://www.staseraintv.com',
        'numberOfPagesToAnalyze': 3, # first 3 pages
    },
    'cb01': {
        'url': 'https://cb01.nagoya',
        'numberOfPagesToAnalyze': 3, # first 3 pages
    },
    'justwatch': {
        'url': 'https://www.justwatch.com',
        'providersQueryParams': ['nfx', 'prv', 'skg', 'pmp', 'rai', 'inf'], # 'Netflix', 'Amazon Prime Video', 'Sky Go', 'Paramount Plus', 'Rai Play', 'Infinity'
        'genresQueryParams': {
#            'commedie': ['cmy', 'eur', 'fml', 'rma'],
#            'azione e avventura': ['act'],
#            'storici e guerra': ['hst', 'war'],
#            'crime e Thriller': ['crm', 'trl'],
#            'scifi': ['scf'],
            'horror': ['hrr'],
#            'fantasy': ['fnt']
        }
    }
}

def createSummaryHtmlFile(summaryPageName, staseraInTvScraperResult, cb01ScraperResult, justwatchScraperResult):
    htmlPageHead = "<!DOCTYPE html><html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'><title>Page Title</title><link rel='stylesheet' href='./ui/css/index.css'><style>.pay-per-view-icon { width: 50px; height: 50px; border-radius: 20%; vertical-align: middle; }</style><script src='./ui/ScrollSnapSlider.js' type='module'></script></head>"
    htmlPageStartBody = "<body><div class='container'>"
    
    # stasera in tv section ::::::::::::::::::::::
    htmlPageStaseraInTv1SerataBody = "<section class='column' aria-labelledby='multiple-heading'><hr><h2 id='multiple-heading'>Stasera in TV</h2><hr><h3>Prima serata</h3><ul class='scroll-snap-slider -multi'>"
    htmlPageStaseraInTv1SerataContentBody = ""
    index1Serata = 0
    for primaSerataItem in staseraInTvScraperResult['primaSerata']:
        # print('primaSerataItem: ', primaSerataItem)
        doubleLiTag = "<li class='scroll-snap-slide' data-index='"+ str(index1Serata) +"'><img height='300' src=" + primaSerataItem['filmImg'] + " width='400'></li><li class='scroll-snap-slide' data-index='" + str(index1Serata+1) + "'><article><p><b>" + primaSerataItem['filmTitle'] + "</b></p><p>" + primaSerataItem['filmDescription'] + "</p><p>" + primaSerataItem['filmTime'] + "</p><p>" + primaSerataItem['filmChannelName'] + "</p><p>" + primaSerataItem['filmChannelsNumber'] + "</p></article></li>"
        htmlPageStaseraInTv1SerataContentBody = htmlPageStaseraInTv1SerataContentBody + doubleLiTag
        index1Serata = index1Serata + 2
    htmlPageStaseraInTv1SerataContentBody = htmlPageStaseraInTv1SerataContentBody + "</ul>"
    htmlPageStaseraInTv2SerataBody = "<h3>Seconda serata</h3><ul class='scroll-snap-slider -multi'>"
    htmlPageStaseraInTv2SerataContentBody = ""
    index2Serata = 0
    for secondaSerataItem in staseraInTvScraperResult['secondaSerata']:
        # print('secondaSerataItem: ', secondaSerataItem)
        doubleLiTag = "<li class='scroll-snap-slide' data-index='"+ str(index2Serata) +"'><img height='300' src=" + secondaSerataItem['filmImg'] + " width='400'></li><li class='scroll-snap-slide' data-index='" + str(index2Serata+1) + "'><article><p><b>" + secondaSerataItem['filmTitle'] + "</b></p><p>" + secondaSerataItem['filmDescription'] + "</p><p>" + secondaSerataItem['filmTime'] + "</p><p>" + secondaSerataItem['filmChannelName'] + "</p><p>" + secondaSerataItem['filmChannelsNumber'] + "</p></article></li>"
        htmlPageStaseraInTv2SerataContentBody = htmlPageStaseraInTv2SerataContentBody + doubleLiTag
        index2Serata = index2Serata + 2
    htmlPageStaseraInTv2SerataContentBody = htmlPageStaseraInTv2SerataContentBody + "</ul></section>"
    
    # cb01 section ::::::::::::::::::::::::::::::::.
    htmlPageCb01Body = "<section class='column' aria-labelledby='multiple-heading'><hr><h2 id='multiple-heading'>CB01</h2><hr><ul class='scroll-snap-slider -multi'>"
    htmlPageCb01ContentBody = ""
    index = 0
    for cb01Item in cb01ScraperResult:
        # print('cb01Item: ', cb01Item)
        doubleLiTag = "<li class='scroll-snap-slide' data-index='"+ str(index) +"'><img height='300' src=" + cb01Item['filmImg'] + " width='400'></li><li class='scroll-snap-slide' data-index='" + str(index+1) + "'><article><p><b>" + cb01Item['filmTitle'] + "</b></p><p>" + cb01Item['filmInfo'] + "</p><p>" + cb01Item['filmDescription'] + "</p><p><a href='" + cb01Item['filmLinks'] + "'>link</a></p></article></li>"
        htmlPageCb01ContentBody = htmlPageCb01ContentBody + doubleLiTag
        index = index + 2
    htmlPageCb01ContentBody = htmlPageCb01ContentBody + "</ul></section>"

    # justwatch section :::::::::::::::::::::::::::::
    if justwatchScraperResult != []:
        htmlPageJustwatchBody = "<section class='column' aria-labelledby='multiple-heading'><hr><h2 id='multiple-heading'>Pay Per View</h2><div style='width=100%;margin:auto;'><img class='pay-per-view-icon' src='https://www.justwatch.com/images/icon/52449861/s100'><img src='https://www.justwatch.com/images/icon/207360008/s100' class='pay-per-view-icon'><img src='https://images.justwatch.com/icon/79172280/s100' class='pay-per-view-icon'><img src='https://images.justwatch.com/icon/3414956/s100' class='pay-per-view-icon'><img src='https://images.justwatch.com/icon/87462522/s100' class='pay-per-view-icon'><img src='https://images.justwatch.com/icon/242706661/s100' class='pay-per-view-icon'></div><hr>"
        htmlPageJustwatchContentBody = ""
        for genreName in justwatchScraperResult:
            htmlPageJustwatchContentBody = htmlPageJustwatchContentBody + "<h3>" + genreName + "</h3><ul class='scroll-snap-slider -multi'>"
            index = 0
            for genreItem in justwatchScraperResult[genreName]:
                doubleLiTag = "<li class='scroll-snap-slide' data-index='"+ str(index) +"'><img height='300' src=" + genreItem['img'] + " width='400'></li><li class='scroll-snap-slide' data-index='" + str(index+1) + "'><article><p><b>" + genreItem['title'] + "</b></p><p>" + genreItem['provider'] + "</p><p>" + genreItem['description'] + "</p></article></li>"
                htmlPageJustwatchContentBody = htmlPageJustwatchContentBody + doubleLiTag
                index = index + 2
            htmlPageJustwatchContentBody = htmlPageJustwatchContentBody + "</ul>"
        htmlPageJustwatchContentBody = htmlPageJustwatchContentBody + "</section>"        
    else: 
        htmlPageJustwatchBody = htmlPageJustwatchContentBody = ''

    # add here other sections

    # html page body closing
    htmlPageCloseTags = "</div></body></html>"

    # final html page composition
    finalHtmlPageTags = htmlPageHead + htmlPageStartBody + htmlPageStaseraInTv1SerataBody + htmlPageStaseraInTv1SerataContentBody + htmlPageStaseraInTv2SerataBody + htmlPageStaseraInTv2SerataContentBody + htmlPageCb01Body + htmlPageCb01ContentBody + htmlPageJustwatchBody + htmlPageJustwatchContentBody + htmlPageCloseTags
    
    # html file management
    file = open(summaryPageName, 'a', encoding="utf-8")
    file.write(finalHtmlPageTags)
    file.close()

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

def getPlatformName():
    # On Android sys.platform returns 'linux', so prefer to check the
    # presence of python-for-android environment variables which start
    # with the prefix 'ANDROID_'.
    
    for key in os.environ:
        if key.startswith('ANDROID_'):
            return 'android'

    if os.environ.get('KIVY_BUILD', '') == 'ios':
        return 'ios'
    elif platform in ('win32', 'cygwin'):
        return 'win'
    elif platform == 'darwin':
        return 'macosx'
    elif platform.startswith('linux'):
        return 'linux'
    elif platform.startswith('freebsd'):
        return 'linux'
    return 'unknown'

# START

# check reachability of URLs of each page to scrape
for scraper in scrapersSetting.keys():
    while not isUrlReachable(scrapersSetting[scraper]['url']):
        print('l\'indirizzo %s' % (scrapersSetting[scraper]['url']), 'potrebbe essere cambiato/errato, controllalo e reinserisci quello corretto: ') 
        scrapersSetting[scraper]['url'] = str(input())

# remove summary page file if It already exists
try:
    os.remove(summaryPageName)
except OSError:
    pass

if getPlatformName() == 'android':
    _thread.start_new_thread(start_server,())

staseraInTvScraperResult = staseraInTvScraper.start(scrapersSetting['staseraInTv'])
cb01ScraperResult = cb01Scraper.start(scrapersSetting['cb01'])
if getPlatformName() != 'android': # necessary because on Android Selenium doesn't work (for now)
    justwatchScraperResult = justwatchScraper.start(scrapersSetting['justwatch'])
else:
    justwatchScraperResult = []
# add here other web site scraper

summaryPageFile = createSummaryHtmlFile(summaryPageName, staseraInTvScraperResult, cb01ScraperResult, justwatchScraperResult)

if getPlatformName() == 'android':
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