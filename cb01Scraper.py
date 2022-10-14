import requests, bs4, os

def getCb01WebPageRawData(pageUrl, pageIndex):
    # set web page url
    newChar = str(pageIndex + 1)
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

    # film infos
    rawFilmInfos = htmlPage.find_all('strong')
    # film titles and links
    rawFilmTitles = htmlPage.find_all('h3', class_='card-title')
    finalRawFilmTitles = []
    rawFilmLinks = []
    for rawTitle in rawFilmTitles:
        aTag = rawTitle.find('a')
        finalRawFilmTitles.append(aTag.text.strip()) # get tag value
        rawFilmLinks.append(aTag['href']) # get tag attribute value
    # film descriptions
    rawFilmContainers = htmlPage.find_all('div', class_='card-content')
    finalRawFilmDescriptions = []
    for rawFilmContainer in rawFilmContainers:
        # "Sibling" in this context is the next node, the next element/tag.
        finalRawFilmDescriptions.append(" ".join((rawFilmContainer.find('br').next_sibling).split()))   
    # film images
    rawFilmImgs = htmlPage.find_all('div', class_='card-image')

    # print('rawFilmInfos: ', rawFilmInfos)
    # print('rawFilmTitles: ', finalRawFilmTitles)
    # print('rawFilmLinks: ', rawFilmLinks)
    # print('rawFilmDescriptions: ', finalRawFilmDescriptions) 
    print('rawFilmImgs: ', rawFilmImgs) 

    return {  
        'rawFilmInfos': rawFilmInfos, 
        'rawFilmTitles': finalRawFilmTitles,
        'rawFilmDescriptions': finalRawFilmDescriptions,
        'rawFilmLinks': rawFilmLinks,
        'rawFilmImgs': rawFilmImgs,
    }

# infos cleaning
def cleanInfos(rawFilmInfos):
    filmInfos = []
    for info in rawFilmInfos:
        genre = info.text.split()[0]
        filmInfos.append(genre)
        
    # print('cleaned infos: ', filmInfos)
    return filmInfos

# titles cleaning
def cleanTitles(rawFilmTitles):
    filmTitles = []
    for title in rawFilmTitles:
        if '[HD]' in title: title = title.replace('[HD]', '', 1)
        if '[Sub-ITA]' in title: filmTitles.append('deleted') 
        else: filmTitles.append(title) 

    # print('cleaned titles: ', filmTitles)
    return filmTitles

# images cleaning
def cleanImgs(rawFilmImgs):
    filmImgs = []
    for divTag in rawFilmImgs:
        # encode space character with %20 if the url include it
        imgUrl = divTag.a.img['src'].replace(" ", "%20")
        filmImgs.append(imgUrl)
    return filmImgs

# add data to summary html page
def addToSummaryPage(currentPageURL, pageIndex, filmTitles, filmDescriptions, filmInfos, filmLinks, filmImgs, summaryPageFile):
    if (pageIndex == 0):
        strTable = "<tr><th colspan='5' style='background-color:blue'>CB01</th></tr>"
    else: 
        strTable = ""

    for i in range(len(filmTitles)):
        if (filmTitles[i] != 'deleted'):
            strRW = "<tr style='background-color:87CEFA'><td><img src=" + filmImgs[i] + " width='115' heght='153'></td><td>" + filmTitles[i] + "</td><td>" + filmInfos[i] + "</td><td>" + filmDescriptions[i] + "</td><td><a href='" + filmLinks[i] + "'>link</a></td></tr>"
            strTable = strTable + strRW
        else:
            continue    
 
    summaryPageFile.write(strTable.strip())

# start
def start(summaryPageFile, cb01BaseURL, numberOfPagesToAnalyze):

    # modify base url for iteration on every page
    cb01URL = cb01BaseURL + '/page/@/'

    # iteration on every page
    for pageIndex in range(numberOfPagesToAnalyze):
        rawWebPageData = getCb01WebPageRawData(cb01URL, pageIndex)
        filmTitles = cleanTitles(rawWebPageData['rawFilmTitles'])
        filmInfos = cleanInfos(rawWebPageData['rawFilmInfos'])
        filmDescriptions = rawWebPageData['rawFilmDescriptions']
        filmLinks = rawWebPageData['rawFilmLinks']
        filmImgs = cleanImgs(rawWebPageData['rawFilmImgs'])
        addToSummaryPage(
            cb01URL, 
            pageIndex, 
            filmTitles, 
            filmDescriptions, 
            filmInfos, 
            filmLinks,
            filmImgs,
            summaryPageFile
        )
