key = ""
endpoint = ""

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt 
import numpy as np

# Authenticate the client using your key and endpoint 
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client

# Example function for detecting sentiment in text
def sentiment_analysis_example(client, comment):
    documents = [comment] #comments
    try:
        response = client.analyze_sentiment(documents=documents)[0]
        overallAnalys =[
            response.confidence_scores.positive,
            response.confidence_scores.neutral,
            response.confidence_scores.negative,
        ]
    except:
      overallAnalys = []
    return overallAnalys
    
def isInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def connect(url):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--log-level=3') ## remove warining
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="C:\chromedriver\chromedriver.exe", chrome_options=options)
    driver.get(url)
    return driver

def load_DOM_elements(class_names, driver):
    parentDOM_elems = []
    for class_name in class_names:
        parentDOM_elems+=driver.find_elements(By.CLASS_NAME, class_name)
    return parentDOM_elems

def parse_elements(domElements, client):
    parseResult = []
    i = 0
    for elem in domElements:
      comment = elem.find_element(By.CLASS_NAME, "text.show-more__control").get_attribute("textContent")
      rating = elem.find_elements(By.TAG_NAME, "span")[1].get_attribute("textContent")
      if(isInt(rating)):
        i+=1
        overall_sen_analys = sentiment_analysis_example(client, comment)
        if(len(overall_sen_analys)>0):
          parseResult.append([comment, int(rating), overall_sen_analys])
          print('\nКоммент(', i, '): ',comment,
          '\nРейтинг: ',int(rating),
          '\nАнализ: ', "Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(overall_sen_analys[0], overall_sen_analys[1], overall_sen_analys[2]))
        else:
          print('\nКоммент(', i, '): AZURE LIMITS!')
    return parseResult

def draw_plot(x_input,y_input,x_label,y_label,title):
    x = np.array(x_input)
    y = np.array(y_input)
    # Here I sort x values and their corresponding y values
    args = np.argsort(x)
    x = x[args]
    y = y[args]
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.scatter(x, y) 
    fit = np.polyfit(x, y, deg=4) 
    p = np.poly1d(fit) 
    plt.plot(x,p(x),"r--") 
    plt.show()

comment_DOM_containers = ['lister-item.mode-detail.imdb-user-review.collapsable','lister-item.mode-detail.imdb-user-review.with-spoiler']
film_urls = ['https://www.imdb.com/title/tt1160419/reviews?ref_=tt_ov_rt']

client = authenticate_client()
for film_url in film_urls:
    driver = connect(film_url)
    commentDOM = load_DOM_elements(comment_DOM_containers, driver)
    statistics = parse_elements(commentDOM, client)
    driver.quit()
    #Plots
    positive=[]
    negative = []
    neutral = []
    rating=[]
    for i in statistics:
        rating_field = i[1]
        rating.append(rating_field)
        analys_field = i[2]
        positive.append(analys_field[0])
        negative.append(analys_field[2])
        neutral.append(analys_field[1])

    draw_plot(positive,rating,"Позитивная тональность","Рейтинг","Зависимость рейтинга от позитивной тональности")
    draw_plot(negative,rating,"Негативная тональность","Рейтинг","Зависимость рейтинга от негативной тональности")
    draw_plot(neutral,rating,"Нейтральная тональность","Рейтинг","Зависимость рейтинга от нейтральной тональности")




