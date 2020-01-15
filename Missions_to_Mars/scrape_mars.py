from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_mars() :
    # initialize the beautiful soup browser
    browser = init_browser()
    
    newsDict = scrapeMarsNews(browser)
    featuredImgDict = scrapeMarsFeaturedImage(browser)
    weatherDict = scrapeMarsWeather(browser)
    factsDict = scrapeMarsFacts(browser)
    hemisImgDict = scrapeHemisphereImages(browser)
    
    # Merge the result dictionaries and return
    mergeDict = { **newsDict, **featuredImgDict, **weatherDict, **factsDict, **hemisImgDict }
    print(f"\n mergeDict = \n{ mergeDict }\n")
    
    # Close the browser after scraping
    browser.quit()

    # Return results
    return mergeDict
    
    
def scrapeMarsNews(browser) :
    print("Scraping Mars News ...")
    
    nasaNews_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(nasaNews_url)
    time.sleep(1)
    
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    
    # results are returned as an iterable list
    news = soup.find_all('div', class_="list_text")
    
    # scrape news date, title, and para
    news_date = news[0].find('div', class_='list_date').contents[0]
    news_title = news[0].find('div', class_='content_title').a.contents[0]
    news_p = news[0].find('div', class_='article_teaser_body').contents[0]

    newsDict = {
        "news_date" : news_date,
        "news_title" : news_title,
        "news_p" : news_p
        }
    
    print(f"\nnewsDict = \n{newsDict}\n")
    return newsDict


def scrapeMarsFeaturedImage(browser) :
    print("Scraping Mars Featured Image ...")
        
    # Visit the url for JPL Featured Space Image
    jplMarsImages_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jplMarsImages_url)
    time.sleep(1)
    
    # Use splinter -  Navigate to the FUll IMAGE page
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1)
    
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    
    # results are returned as an iterable list
    featured = soup.find_all('div', class_="fancybox-wrap")
 
    #  find the image url for the current Featured Mars Image
    featured_img = featured[0].find('div', class_='fancybox-inner')
    featured_image_url = featured_img.img['src']
    
    #  find the image title for the current Featured Mars Image
    featured_image_title = featured[0].find('div', class_='fancybox-title').contents[0]
    
    featuredImageDict = {
        "featured_image_url" : featured_image_url,
        "featured_image_title" : featured_image_title
        }
    
    print(f"\nfeaturedImageDict = \n{featuredImageDict}\n")
    return featuredImageDict

def scrapeMarsWeather(browser) :
    print("Scraping Mars Weather ...")
        
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    time.sleep(1)
    
    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    
    # results are returned as an iterable list
    tweets= soup.find_all('div', class_="tweet")
    
    mars_weather = tweets[0].p.contents[0]
    weatherDict = { "mars_weather" : mars_weather}
    
    print(f"\nweatherDict = \n{weatherDict}\n")
    return weatherDict

def scrapeMarsFacts(browser) :
    print("Scraping Mars Facts ...")
        
    marsFacts_url = 'https://space-facts.com/mars/'

    #read facts table from the site
    factsTables = pd.read_html(marsFacts_url)
    
    # clean facts table in Pandas 
    df = factsTables[0]
    df.columns = ['parameter', 'value']
    df.set_index('parameter', inplace=True)
    
    # generate and clean up html facts table
    html_factsTable = df.to_html()
    html_factsTable = html_factsTable.replace('\n', '')

    # create a dict to return
    factsDict = { "html_factsTable" : html_factsTable}
    
    print(f"\nfactsDict = \n{factsDict}\n")
    return factsDict

def scrapeHemisphereImages(browser) :
    print("Scraping Hemisphere Images ...")

    astrogeo_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(astrogeo_url)
    time.sleep(1)
    
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    
    hemisphere_image_urls = []
    items = soup.find_all('div', class_='item')

    for item in items :
        link = item.a
        href=link['href']
        linkURL = 'https://astrogeology.usgs.gov' + href

        #print(linkURL)

        #brute force visit link url since broswer.click_link_by_href is erroring out
        browser.visit(linkURL)
        soup = BeautifulSoup(browser.html, 'html.parser')
        time.sleep(1)

        h2 = soup.find('h2', class_='title')
        title=h2.contents[0]

        imglink = soup.find('div', class_='downloads').a
        img_url = imglink['href']

        #print(image_url)
        imgDict = { 'title' : title, 'url' : img_url}
        hemisphere_image_urls.append(imgDict)
    
    hemisImgDict = { "hemisphere_image_urls" : hemisphere_image_urls } 
    
    print(f"\nhemisImgDict = \n{hemisImgDict}\n")
    return hemisImgDict

#test the scraping
scrape_mars()
