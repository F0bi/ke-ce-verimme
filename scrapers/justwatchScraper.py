import requests, bs4, time, os
from selenium import webdriver

def createGenrePageURL(baseQueryURL, genreQueryParams):
    genreParams = ''
    for param in genreQueryParams:
        genreParams = genreParams + param + ','
    genreParams = genreParams[:-1] # remove last comma    
    genreURL = baseQueryURL.replace('placeholder', genreParams)
    # print('genreURL: ', genreURL)
    return genreURL

def createBaseURL(justwatchBaseURL, providersQueryParams):
    baseURL = justwatchBaseURL + '/it?genres=placeholder&providers='
    for param in providersQueryParams:
        baseURL = baseURL + param + ','
    baseURL = baseURL[:-1] # remove last comma
    baseURL = baseURL + '&release_year_from=2022&sort_by=release_year'
    # print('baseURL: ', baseURL)
    return baseURL

def getGenrePageDataPaths(pageSource):
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

def scrollGenrePageToTheEnd(genreURL):
    # for future support of Selenium on Android via Pydroid
    path_to_chromedriver = os.path.dirname(__file__) + '/chromedriver'
    print('path_to_chromedriver: ', path_to_chromedriver)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('androidPackage', 'com.android.chrome')
    driver = webdriver.Chrome(path_to_chromedriver, 0, options=options)
    driver.get('https://google.com')
    driver.quit()

    # service = Service(path_to_chromedriver)
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option('androidPackage', 'com.android.chrome')
    # driver = webdriver.Chrome(service=service, options=options)
    
    # driver = webdriver.Chrome() # from desktop
    driver.get(genreURL)

    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
    return driver.page_source        

def getGenrePageData(justwatchBaseURL, genrePaths):
    finalData = []
    i = 0
    for path in genrePaths:
        singleDataItem = {
            "img": None,
            "title": None,
            "description": None,
            "provider": None,
        }
        res = requests.Response()
        trycnt = 3  # max try cnt
        while trycnt > 0:
            try:
                # get html page content as string
                res = requests.get(justwatchBaseURL + path)
                res.raise_for_status()
                trycnt = 0 # success
            except requests.HTTPError as exc:
                if trycnt <= 0: 
                    print("Failed to retrieve: " + path + "\n" + str(exc))  # done retrying
                else:
                    trycnt -= 1  # retry
                    if res.status_code == 429: # to many requests
                        time.sleep(5)  # wait 4 seconds then retry
                    else:  
                        time.sleep(0.5)  # wait 1/2 second then retry
        # go to next URL

        # generate page DOM structure from string format
        htmlPage = bs4.BeautifulSoup(res.text, 'html.parser') # type: ignore
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
        MAX_DESCRIPTION_LEN = 270
        pTag = htmlPage.find('p', class_='text-wrap-pre-line mt-0')
        if pTag is None:
            singleDataItem['description'] = 'Non presente' # type: ignore
        else: 
            spanTag = pTag.contents[0] # type: ignore
            singleDataItem["description"] = spanTag.text.strip() # type: ignore
            if len(singleDataItem["description"]) >= MAX_DESCRIPTION_LEN:
                singleDataItem["description"] = singleDataItem["description"][0:MAX_DESCRIPTION_LEN+1] + '...' # type: ignore
        # provider
        divTag = htmlPage.find('div', class_='price-comparison__grid__row price-comparison__grid__row--stream price-comparison__grid__row--block')
        if divTag is None:
            singleDataItem["provider"] = 'Non presente' # type: ignore
        else:
            imgTag = divTag.find('img') # type: ignore
            singleDataItem["provider"] = imgTag['title'] # type: ignore
        # check
        i = i + 1
        print(i, ' ', path, ' ', res, ' ', singleDataItem["title"], ' ', singleDataItem["provider"])
         # add item
        finalData.append(singleDataItem) 

    return finalData    

# start
def start(justwatchScaperSettings):
    # extract scraper settings
    justwatchBaseURL = justwatchScaperSettings['url']
    providersQueryParams = justwatchScaperSettings['providersQueryParams']
    genresQueryParams = justwatchScaperSettings['genresQueryParams']
    #
    baseURL = createBaseURL(justwatchBaseURL, providersQueryParams)
    #
    result = {}
    for genreKey in genresQueryParams:
        print('genre: ', genreKey)
        genrePageURL = createGenrePageURL(baseURL, genresQueryParams[genreKey])
        scrolledGenrePage = scrollGenrePageToTheEnd(genrePageURL)
        genrePageDataPaths = getGenrePageDataPaths(scrolledGenrePage)
        result[genreKey] = getGenrePageData(justwatchBaseURL, genrePageDataPaths)

    # print('result: ', result)
    return result
