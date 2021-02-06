from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from decimal import Decimal
import decimal 
import os, sys
import datetime
import time
import locale
import requests
import argparse
import socketio
import json
import pandas as pd
import mysql.connector # pip install mysql-connector-python
from dateutil.parser import parse
from sqlalchemy import Numeric
from sqlalchemy import Date
import dateparser # pip install dateparser # setx path "%path%;C:\Program Files (x86)\Microsoft Visual C++ Build Tools"

#pip install mysql-connector
#import MySQLdb
# Connect to server
import keyring
#keyring.set_password("system", "quant", "")
pw = keyring.get_password("system", "quant")
#locale.setlocale(locale.LC_ALL, 'german')
locale.setlocale(locale.LC_ALL, 'german')

from sqlalchemy import create_engine

#cnx = MySQLdb.connect("nuc.lan","quant",pw,"quant" )
engine = create_engine('mysql+mysqlconnector://quant:'+pw+'@nuc.lan/quant', echo=False)

cnx = mysql.connector.connect(
    host="nuc.lan",
    port=3306,
    user="quant",
    password=pw,
    database="quant")

# Get a cursor



calledTimes = 0

#Table Structure


def dataframeFromMySQL(MysqlConn,WKN):
    return 0

def dataframeToMySQL(df,MysqlConn,WKN):
    

    df['wkn'] = WKN
    df.to_sql(con=MysqlConn, name='StockQuotesDailyDF', if_exists='append',  dtype={"Date": Date(), "Open": Numeric(precision=4, scale=2, decimal_return_scale=2),"High": Numeric(),"Low": Numeric(),"Close": Numeric()})
    # Execute a query
    #cur.execute("SELECT CURDATE()")

    # Fetch one result
    #row = cur.fetchone()
    #print("Current date is: {0}".format(row[0]))


    #cur.execute("SHOW VARIABLES LIKE '%version%'")
    #remaining_rows = cur.fetchall()
    # Close connection
    


    #INSERT INTO `StockQuotesDaily`(`isin`, `name`, `symbol`, `qdate`, `open`, `high`, `low`, `close`, `volume`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7],[value-8],[value-9])
    return 0


def getTableValuesOnePage(driver,ec):
    global calledTimes
    
    df = pd.DataFrame(
    {"Date" : [],
    "Open" : [],
    "High" : [],
    "Low" : [],
    "Close" : [],
    "Volume" : []
    })


    cnt = 0

    calledTimes = calledTimes + 1
    print('calledTimes: '+str(calledTimes))
    try:
        table = WebDriverWait(driver, 60).until(ec.presence_of_all_elements_located((By.XPATH, './/*[@id="id_pricedata-layer"]/div/div[2]/div/div/div/div/div/div/div[2]/table')))
        
        #table = driver.find_elements_by_xpath('.//*[@id="id_pricedata-layer"]/div/div[2]/div/div/div/div/div/div/div[2]/table')
        #time.sleep(2)

        #table = driver.find_elements_by_class_name('table table--collapse-sm display table--mobile-table')
        WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.CLASS_NAME, 'table__column--top')))
    
        recordss = table[0].find_elements_by_class_name('table__column--top')
        recordcopy = []
        #records = recordss.copy()
        for record in recordss:
            recordcopy.append(record.text)
            
        
        for record in recordcopy:

            #print('cnt: '+str(cnt))
            #print(record)
            ccount = cnt % 6
            if ccount == 0:
                #print('Date: ' + record.text)
                
                dt = dateparser.parse(record, languages=['de'])
                #c = parse(record)
                Date = dt #Date(record.text) .strftime('%Y-%m-%d')
                
            if ccount == 1:
                #print('Open: ' + record.text)
                Open = locale.atof(record, decimal.Decimal)
            if ccount == 2:
                #print('High: ' + record.text)
                High = locale.atof(record, decimal.Decimal)
            if ccount == 3:
                #print('Low: ' + record.text)
                Low = locale.atof(record, decimal.Decimal)
            if ccount == 4:
                #print('Close: ' + record.text)
                Close = locale.atof(record, decimal.Decimal)
            if ccount == 5:
                #print('Volume: ' + record.text)
                Volume = record
                if "Mio." in Volume:
                    vpre= Volume.split('Mio.')[0]
                    vpre = int(vpre) * 1000000
                    Volume = vpre


            if ccount == 5:       
                dfTmp = pd.DataFrame(
                {"Date" : [Date],
                "Open" : [Open],
                "High" : [High],
                "Low" : [Low],
                "Close" : [Close],
                "Volume" : [Volume]
                })
                df = df.append(dfTmp)


                

            cnt = (cnt + 1)
    except (TimeoutException):
        print("end of pagination")
        return (df.count(),df)

    return  (cnt,df) 

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--wkn')
args = parser.parse_args()
wkn = args.wkn

#locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8') # 
print(os.getcwd())



chrome_options = Options()
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--no-sandbox") # linux only
#chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works


path = os.path.dirname(os.path.abspath(__file__))
prefs = {"download.default_directory":path}

chrome_options.add_experimental_option("prefs", prefs)


driver = webdriver.Chrome(os.getcwd()+"\\chromedriver.exe",options=chrome_options) #C:\\Users\\d047102\\Desktop\\DemoDataGrabber
#//*[@id="app--idDemoSearchField-inner"]

driver.get("https://www.comdirect.de/inf/index.html")
#driver.maximize_window()
#driver.implicitly_wait(2)
# /html/body/div[6]/div[2]/div/div[2]/div[1]/button
YesButton = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, './/html/body/div[6]/div[2]/div/div[2]/div[1]/button')))
#YesButton = driver.find_elements_by_xpath('.//*[@id="uc-btn-accept-banner"]')

YesButton.click()

searchField = driver.find_elements_by_xpath('.//*[@id="search_form"]/input')
print("Element is visible? " + str(searchField[0].is_displayed()))

searchField[0].send_keys(wkn)

searchButton = driver.find_elements_by_xpath('.//*[@id="search_form"]/a')

searchButton[0].click()




WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.LINK_TEXT, 'Chart')))




selectMarket = driver.find_elements_by_xpath('.//*[@id="marketSelect"]')
if len(selectMarket) > 0:
    selectMarket[0]
    Select(selectMarket[0]).select_by_visible_text('Xetra')


time.sleep(2)
driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.LINK_TEXT, 'Chart'))))
time.sleep(1)
ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "body > div.cif-scope-content-wrapper.siteFrame.advertising-scope > div > div:nth-child(2) > div.col__content.col__content--no-padding.hidden-print.bg-color--cd-black-7 > div > div > div > div.button-group__container.hidden-sm > a:nth-child(4) > span")))).click().perform()

driver.implicitly_wait(5)


time.sleep(2)
driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.LINK_TEXT, 'Max'))))
time.sleep(1)
ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#chartForm > div.button-area.outer-spacing--none > div > div > div.button-group__container.hidden-sm.hidden-md > a:nth-child(8) > span")))).click().perform()

#time.sleep(2)


time.sleep(2)
driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.LINK_TEXT, 'Kursdaten'))))
time.sleep(1)
ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#openQuoteListButton")))).click().perform()

#time.sleep(2)
#driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.LINK_TEXT, 'Daten für Excel (csv) exportieren'))))
#time.sleep(1)
#demos = driver.find_elements_by_class_name('coverpic-desc-icons-asset-role') 
#ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#id_pricedata-layer > div > div.layer__content.layer__content--wider-lg > div > div > div > div > div > div > div.button-area.button-area--single-right > div > a > span")))).click().perform()

#//*[@id="id_pricedata-layer"]/div/div[2]/div/div/div/div/div/div/div[3]/div[1]/div[2]

cur = cnx.cursor()
cur.execute("DELETE FROM `StockQuotesDailyDF` WHERE `wkn`='"+str(wkn)+"'" )

cnx.commit()

print(cur.rowcount, "record(s) deleted")
cnx.close()

recordcount = -1
while recordcount != 0:
    (recordcount,df) = getTableValuesOnePage(driver,ec)
    print('recordcount: ' + str(df.count()))
    try:
        dataframeToMySQL(df.copy(),engine,wkn)
    except StaleElementReferenceException as e:
        print(e)
        (recordcount,df) = getTableValuesOnePage(driver,ec)
        print('after stale recordcount: ' + str(df.count()))
        dataframeToMySQL(df.copy(),engine,wkn)
          
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.CLASS_NAME, 'icon__svg'))))
    
    if recordcount > 0: ## then this timeout here marks the end

        ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, './/*[@id="id_pricedata-layer"]/div/div[2]/div/div/div/div/div/div/div[3]/div[1]/div[2]')))).click().perform()
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.XPATH, './/*[@id="FORM_KURSDATEN"]/div[3]'))))


#cnx.close()




