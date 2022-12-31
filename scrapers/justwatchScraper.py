import json
import requests, bs4
from selenium import webdriver
import time

def createComedyURL(baseQueryURL, comedyQueryParams):
    comedyParams = ''
    for param in comedyQueryParams:
        comedyParams = comedyParams + param + ','
    comedyParams = comedyParams[:-1] # remove last comma    
    comedyURL = baseQueryURL.replace('placeholder', comedyParams)
    print('comedyURL: ', comedyURL)
    return comedyURL

def createBaseURL(justwatchBaseURL, providersQueryParams):
    baseURL = justwatchBaseURL + '/it?genres=placeholder&providers='
    for param in providersQueryParams:
        baseURL = baseURL + param + ','
    baseURL = baseURL[:-1] # remove last comma
    baseURL = baseURL + '&release_year_from=2022&sort_by=release_year'
    # print('baseURL: ', baseURL)
    return baseURL

def getGenrePaths(pageSource):
    # generate page DOM structure from string format
    htmlPage = bs4.BeautifulSoup(pageSource, 'html.parser')
    # print('comedy html page 1: ', htmlPage)
    grid = htmlPage.find_all('div', class_='title-list-grid')
    # print('grid: ', grid)
    aTags = htmlPage.find_all('a', class_='title-list-grid__item--link')
    # print('comedy aTags: ', aTags)
    i = 0
    genrePaths = []
    for aTag in aTags:
        # i = i + 1
        # print(i, ': ', aTag['href']) # get tag attribute value
        genrePaths.append(aTag['href'])
    
    return genrePaths

def scrollPageToTheEnd(genreURL):
    browser = webdriver.Chrome()
    browser.get(genreURL)

    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
    return browser.page_source        

def getGenreRawData(justwatchBaseURL, genrePaths):
    finalData = []
    singleDataItem = {
        "img": None,
        "title": None,
        "description": None,
        "provider": None,
    }

    for path in genrePaths:
        res = requests.Response()
        trycnt = 3  # max try cnt
        while trycnt > 0:
            try:
                print('final Page URL: ', justwatchBaseURL + path)
                # get html page content as string
                res = requests.get(justwatchBaseURL + path)
                trycnt = 0 # success
            except Exception as exc:
                if trycnt <= 0: print("Failed to retrieve: " + path + "\n" + str(exc))  # done retrying
                else: trycnt -= 1  # retry
                time.sleep(0.5)  # wait 1/2 second then retry
        # go to next URL

        # generate page DOM structure from string format
        htmlPage = bs4.BeautifulSoup(res.text, 'html.parser')
        # img
        pictureTag = htmlPage.find('picture', class_='picture-comp title-poster__image')
        if pictureTag is None:
            singleDataItem["img"] = 'Non presente' # type: ignore
        else:    
            sourceTag = pictureTag.contents[0] # type: ignore
            singleDataItem["img"] = sourceTag['data-srcset'].split(', ')[0] # type: ignore
        # title
        h1Tag = htmlPage.find('h1')
        if h1Tag is None:
            singleDataItem["title"] = 'Non presente' # type: ignore
        else:    
            singleDataItem["title"] = h1Tag.text.strip() # type: ignore
        # description
        pTag = htmlPage.find('p', class_='text-wrap-pre-line mt-0')
        if pTag is None:
            singleDataItem['description'] = 'Non presente' # type: ignore
        else: 
            spanTag = pTag.contents[0] # type: ignore
            singleDataItem["description"] = spanTag.text.strip() # type: ignore
        # provider
        pictureTag = htmlPage.find('picture', class_='provider-icon')
        if pictureTag is None:
            singleDataItem["provider"] = 'Non presente' # type: ignore
        else:    
            imgTag = pictureTag.contents[1] # type: ignore
            singleDataItem["provider"] = imgTag['title'] # type: ignore
        # check
        # print('singleDataItem: ', singleDataItem)
        # add item
        finalData.append(singleDataItem)

    return finalData    

# start
def start(justwatchScaperSettings):
    # extract scraper settings
    justwatchBaseURL = justwatchScaperSettings['url']
    providersIdentifierToAnalyze = justwatchScaperSettings['providersIdentifierToAnalyze']
    providersQueryParams = justwatchScaperSettings['providersQueryParams']
    comedyQueryParams = justwatchScaperSettings['comedyQueryParams']
    actionAndAdventureQueryParams = justwatchScaperSettings['actionAndAdventureQueryParams']
    historicalAndWarQueryParams = justwatchScaperSettings['historicalAndWarQueryParams']
    crimeAndThrillerQueryParams = justwatchScaperSettings['crimeAndThrillerQueryParams']
    scifiQueryParams = justwatchScaperSettings['scifiQueryParams']
    horrorQueryParams = justwatchScaperSettings['horrorQueryParams']
    fantasyQueryParams = justwatchScaperSettings['fantasyQueryParams']
  
    baseURL = createBaseURL(justwatchBaseURL, providersQueryParams)
    comedyURL = createComedyURL(baseURL, comedyQueryParams)
    scrolledPage = scrollPageToTheEnd(comedyURL)
    genrePaths = getGenrePaths(scrolledPage)
    genreRawData = getGenreRawData(justwatchBaseURL, genrePaths)

    # print('PIPPO: ', genreRawData)
        