import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.facebook.com/profile.php?id=100090573221915")
driver.quit()