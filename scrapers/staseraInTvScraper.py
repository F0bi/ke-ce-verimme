import requests, bs4, os

def getStaseraInTvWebPageRawData(pageUrl, pageIndex):
    if (pageIndex == 0): newChar = '' 
    else: newChar = str(pageIndex + 1)
    finalPageUrl = pageUrl.replace('@', newChar, 1)    

    # get html page content as string
    res = requests.get(finalPageUrl)
    # check 
    try:
        res.raise_for_status()
    except Exception as exc:
        print('Error: %s' % (exc))    
    # generate page DOM structure from string format
    htmlPage = bs4.BeautifulSoup(res.text, 'html.parser'); 
    # scrap raw data
    filmsContainer = htmlPage.find('div', class_='chpreviewbox')
    rawFilmChannelsNames = filmsContainer.find_all('a')
    rawFilmChannelsNumbers = filmsContainer.find_all('chnum')
    rawFilmTimes = filmsContainer.find_all('big')
    rawFilmTitles = filmsContainer.find_all('span')
    rawFilmImgs = filmsContainer.find_all('small')
    
    # print('rawFilmChannelsNames: ', rawFilmChannelsNames)
    # print('rawFilmChannelsNumbers: ', rawFilmChannelsNumbers)
    # print('rawFilmTimes: ', rawFilmTimes)
    # print('rawFilmTitles: ', rawFilmTitles)
    # print('rawFilmImgs: ', rawFilmImgs)

    return { 
        'rawFilmChannelsNames': rawFilmChannelsNames, 
        'rawFilmChannelsNumbers': rawFilmChannelsNumbers, 
        'rawFilmTimes': rawFilmTimes, 
        'rawFilmTitles': rawFilmTitles,
        'rawFilmImgs': rawFilmImgs
    }

# channels names cleaning
def cleanChannelsNames(rawFilmChannelsNames):
    filmChannelsNames = []
    for channelName in rawFilmChannelsNames:
        if channelName.text != '' and channelName.text != '[continua]' and channelName.text.strip() != 'Prima TV':
            filmChannelsNames.append(channelName.text.strip()) 

    # print('cleaned channels names: ', filmChannelsNames)
    return filmChannelsNames

# channels numbers cleaning
def cleanChannelsNumbers(rawFilmChannelsNumbers):
    filmChannelsNumbers = []
    for channelNumber in rawFilmChannelsNumbers:
        filmChannelsNumbers.append(channelNumber.text.strip()) 

    # print('cleaned channels numbers: ', filmChannelsNumbers)
    return filmChannelsNumbers    

# times cleaning
def cleanTimes(rawFilmTimes):
    filmTimes = []
    for time in rawFilmTimes:
        finalTime = time.find('big')
        if finalTime != None:
            filmTimes.append(finalTime.text.strip()) 

    # print('cleaned times: ', filmTimes)
    return filmTimes

# titles cleaning
def cleanTitles(rawFilmTitles):
    filmTitles = []
    for title in rawFilmTitles:
        if title.text.strip() != '':
            filmTitles.append(title.text.strip()) 

    # print('cleaned titles: ', filmTitles)
    return filmTitles

# images cleaning
def cleanImgs(rawFilmImgs, staseraInTvBaseURL):
    filmImgs = []
    for smallTag in rawFilmImgs:
        # encode space character with %20 if the url include it
        imgUrl = smallTag.span.a.img['src'].replace(" ", "%20")
        filmImgs.append(staseraInTvBaseURL + imgUrl)

    # print('cleaned imgs: ', filmImgs)    
    return filmImgs    

# add data to summary html page
def addToSummaryPage(currentPageURL, staseraInTv1SerataURL, pageIndex, filmTitles, filmTimes, filmChannelsNames, filmChannelsNumbers, filmImgs, summaryPageFile):
  
    if (currentPageURL == staseraInTv1SerataURL): 
        if (pageIndex == 0):
            siteRowStr = "<tr><th colspan='5' style='background-color:green'>Stasera in TV</th></tr><tr><th colspan='5'>Prima serata</th></tr>"
        else: 
            siteRowStr = ""
    elif (pageIndex == 0):
        siteRowStr = "<tr><th colspan='5'>Seconda serata</th></tr>"
    else: siteRowStr = ""

    for i in range(len(filmTitles)):
        filmRowStr = "<tr style='background-color:B1E8B2'><td><img src=" + filmImgs[i] + "></td><td>" + filmTitles[i] + "</td><td>" + filmTimes[i] + "</td><td>" + filmChannelsNames[i] + "</td><td>" + filmChannelsNumbers[i] + "</td></tr>"
        siteRowStr = siteRowStr + filmRowStr
 
    summaryPageFile.write(siteRowStr)

# start
def start(summaryPageFile, staseraInTvBaseURL, numberOfPagesToAnalyze):
    # modify base url for iteration on every page
    staseraInTv1SerataURL = staseraInTvBaseURL + '/index@.html'
    staseraInTv2SerataURL = staseraInTvBaseURL + '/seconda_serata_stasera@.html'
    
    # iteration on every page
    for serataIndex in range(2):
        if (serataIndex == 0): currentStaseraInTvURL = staseraInTv1SerataURL
        else: currentStaseraInTvURL = staseraInTv2SerataURL 
        for pageIndex in range(numberOfPagesToAnalyze):
            rawWebPageData = getStaseraInTvWebPageRawData(currentStaseraInTvURL, pageIndex)
            filmChannelsNames = cleanChannelsNames(rawWebPageData['rawFilmChannelsNames'])
            filmChannelsNumbers = cleanChannelsNumbers(rawWebPageData['rawFilmChannelsNumbers'])
            filmTitles = cleanTitles(rawWebPageData['rawFilmTitles'])
            filmTimes = cleanTimes(rawWebPageData['rawFilmTimes'])
            filmImgs = cleanImgs(rawWebPageData['rawFilmImgs'], staseraInTvBaseURL)
            addToSummaryPage(
                currentStaseraInTvURL, 
                staseraInTv1SerataURL, 
                pageIndex, 
                filmTitles, 
                filmTimes, 
                filmChannelsNames, 
                filmChannelsNumbers,
                filmImgs,
                summaryPageFile
            )
