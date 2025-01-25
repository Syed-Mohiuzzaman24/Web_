# import os
# import mysql.connector
# from mysql.connector import Error
# # from db_connection import create_db_connection
# from app.db_connection import create_db_connection 
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from app import news_insert
# from datetime import date

# # Base URL for the website
# base_url = "https://www.tbsnews.net"

# def execute_query(connection, query):
#     """
#     Execute a given SQL query on the provided database connection.

#     Parameters
#     ----------
#     connection : mysql.connector.connection.MySQLConnection
#         The connection object to the database.
#     query : str
#         The SQL query to execute.

#     Returns
#     -------
#     None
#     """
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         connection.commit()
#         print("Query successful")
#     except Error as e:
#         print(f"The error '{e}' occurred")

# def execute_read_query(connection, query):
#     """
#     Execute a read query and return the results.

#     Parameters
#     ----------
#     connection : mysql.connector.connection.MySQLConnection
#         The connection object to the database.
#     query : str
#         The SQL query to execute.

#     Returns
#     -------
#     list
#         A list of tuples containing the rows returned by the query.
#     """
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         result = cursor.fetchall()
#         return result
#     except Error as e:
#         print(f"The error '{e}' occurred")
#         return []

# # Request the main page
# response = requests.get(f"{base_url}/economy/stocks")
# if response.status_code != 200:
#     print("Failed to retrieve the main page")
#     exit()

# soup = BeautifulSoup(response.text, 'html.parser')

# # Scrape the news cards
# news_cards = soup.find_all('div', class_='card relative')
# if not news_cards:
#     print("No news cards found.")
#     exit()

# # Establish database connection
# conn = create_db_connection()

# # Use a default editor ID that we know exists in the editors table
# DEFAULT_EDITOR_ID = 1  # Make sure this ID exists in your editors table
# CATEGORY_NAME = "Stocks"  # Set the category name dynamically if needed
# CATEGORY_DESCRIPTION = "News related to the stock market."

# # Ensure editor exists or create one
# editor_id = DEFAULT_EDITOR_ID
# # Check if editor with this ID exists
# editor_check_query = f"SELECT id FROM editors WHERE id = {editor_id};"
# existing_editor = execute_read_query(conn, editor_check_query)

# if not existing_editor:
#     # If editor does not exist, insert a default editor
#     editor_name = "Default Editor"
#     editor_email = "default.editor@example.com"
#     insert_editor_query = f"""
#     INSERT INTO editors (id, name, email) 
#     VALUES ({editor_id}, '{editor_name}', '{editor_email}');
#     """
#     execute_query(conn, insert_editor_query)
#     print(f"Inserted default editor with ID {editor_id}")

# for card in news_cards:
#     # Extract title
#     title_tag = card.find('h3', class_='card-title')
#     title = title_tag.get_text(strip=True) if title_tag else "No title found"

#     # Extract URL
#     link_tag = card.find('a', href=True)
#     relative_url = link_tag['href'] if link_tag else None
#     full_url = f"{base_url}{relative_url}" if relative_url else None

#     # Skip if URL is missing
#     if not full_url:
#         print(f"Skipping news without a URL: {title}")
#         continue

#     # Request each news page to extract more details
#     news_response = requests.get(full_url)
#     if news_response.status_code != 200:
#         print(f"Failed to retrieve news details for: {full_url}")
#         continue

#     news_soup = BeautifulSoup(news_response.text, 'html.parser')

#     # Extract description: Collect all <p> tags inside the <article> element
#     article_tag = news_soup.find('article')
#     description = ""
#     if article_tag:
#         paragraphs = article_tag.find_all('p')
#         description = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
#     else:
#         description = "No description found."

#     # Extract author name
#     author_div = news_soup.select_one('div.author-name strong.color-black')
#     author = author_div.get_text(strip=True) if author_div else "Unknown Author"

#     # Extract publish date
#     publish_date_div = news_soup.find('div', class_='date')
#     publish_date = (
#         publish_date_div.get_text(strip=True).split('Last modified:')[0].strip()
#         if publish_date_div
#         else "No publish date found"
#     )
#     publish_date = " ".join(publish_date.split()[:3])
#     publish_date = publish_date.replace("Sign In", "").replace("Sign", "").strip()
#     date_string = publish_date

#     current_date = date.today()

#     # Extract last modified date
#     last_modified_div = news_soup.find_all('div', class_='date')
#     last_modified_date = (
#         last_modified_div[-1].get_text(strip=True).replace('Last modified:', '').strip()
#         if len(last_modified_div) > 1
#         else "No last modified date found"
#     )

#     # Check if author exists
#     author_id = news_insert.get_author_id(connection=conn, name=author)

#     # If author doesn't exist, create new author
#     if not author_id:
#         try:
#             author_email = f"{author.replace(' ', '')}@gmail.com"
#             news_insert.insert_author(connection=conn, name=author, email=author_email)
#             author_id = news_insert.get_author_id(connection=conn, name=author)
#         except Exception as e:
#             print(f"Error inserting author: {e}")
#             author_id = 1  # Default author ID

#     # Insert news
#     try:
#         news_insert.insert_news(
#             connection=conn,
#             category_id=1,
#             author_id=author_id,
#             editor_id=DEFAULT_EDITOR_ID,  # Use default editor ID now confirmed to exist
#             datetime=current_date,
#             title=title,
#             body=description,
#             link=full_url
#         )
#         print(f"Successfully inserted news: {title}")
#     except Exception as e:
#         print(f"Error inserting news: {e}")

# # Close database connection
# conn.close()






# import datetime
# from requests_html import HTMLSession
# from .database import SessionLocal
# from .crud import create_news
# from .schemas import NewsCreate, News

# def single_news_scraper(url: str):
#     session = HTMLSession()
#     try:
#         response = session.get(url)
#         # response.html.render()  # This will download Chromium if not found

#         publisher_website = url.split('/')[2]
#         publisher = publisher_website.split('.')[-2]
#         title = response.html.find('h1', first=True).text
#         reporter = response.html.find('.contributor-name', first=True).text
#         datetime_element = response.html.find('time', first=True)
#         news_datetime = datetime_element.attrs['datetime']
#         category = response.html.find('.print-entity-section-wrapper', first=True).text
#         content = '\n'.join([p.text for p in response.html.find('p')])
#         img_tags = response.html.find('img')
#         images = [img.attrs['src'] for img in img_tags if 'src' in img.attrs]
#         news_datetime = datetime.datetime.now()

#         print(f"Scraped news from {url}")
#         print(f"Title: {title}")
#         print(f"Reporter: {reporter}")
#         print(f"Date: {news_datetime}")
#         print(f"Category: {category}")
#         print(f"Images: {images}")


#         return NewsCreate(
#             publisher_website=publisher_website,
#             news_publisher=publisher,
#             title=title,
#             news_reporter=reporter,
#             datetime=news_datetime,
#             link=url,
#             news_category=category,
#             body=content,
#             images=images,
#         )
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         session.close()

# def scrape_and_store_news(url: str, db: SessionLocal):
#     # db = SessionLocal()
#     news_data = single_news_scraper(url)
#     print(news_data)
#     inserted_news = ""
#     if news_data:
#         # print(news_data)
#         inserted_news = create_news(db=db, news=news_data)
#     db.close()

#     return inserted_news

import datetime
from requests_html import HTMLSession
from .database import SessionLocal
from .crud import create_news
from .schemas import NewsCreate

def single_news_scraper(url: str):
    """
    Scrape a single news article from the given URL.

    Parameters
    ----------
    url : str
        The URL of the news article to scrape.

    Returns
    -------
    NewsCreate or None
        A NewsCreate object containing the scraped data, or None if scraping fails.
    """
    session = HTMLSession()
    try:
        response = session.get(url)
        
        # Parse news details
        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]
        title = response.html.find('h1', first=True).text if response.html.find('h1', first=True) else "No title found"
        reporter = response.html.find('.contributor-name', first=True).text if response.html.find('.contributor-name', first=True) else "Unknown Reporter"
        datetime_element = response.html.find('time', first=True)
        news_datetime = datetime_element.attrs['datetime'] if datetime_element else datetime.datetime.now()
        category = response.html.find('.print-entity-section-wrapper', first=True).text if response.html.find('.print-entity-section-wrapper', first=True) else "Uncategorized"
        content = '\n'.join([p.text for p in response.html.find('p')])
        img_tags = response.html.find('img')
        images = [img.attrs['src'] for img in img_tags if 'src' in img.attrs]

        print(f"Scraped news from {url}")
        print(f"Title: {title}")
        print(f"Reporter: {reporter}")
        print(f"Date: {news_datetime}")
        print(f"Category: {category}")
        print(f"Images: {images}")

        return NewsCreate(
            publisher_website=publisher_website,
            news_publisher=publisher,
            title=title,
            news_reporter=reporter,
            datetime=news_datetime,
            link=url,
            news_category=category,
            body=content,
            images=images,
        )
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return None
    finally:
        session.close()

def scrape_and_store_news(url: str, db: SessionLocal):
    """
    Scrape a news article and store it in the database.

    Parameters
    ----------
    url : str
        The URL of the news article to scrape.
    db : SessionLocal
        The database session for storing the scraped data.

    Returns
    -------
    News or None
        The inserted news object, or None if scraping or insertion fails.
    """
    news_data = single_news_scraper(url)

    if news_data:
        try:
            inserted_news = create_news(db=db, news=news_data)
            print(f"Successfully inserted news: {inserted_news.title}")
            return inserted_news
        except Exception as e:
            print(f"An error occurred while storing the news: {e}")
            return None
    else:
        print("No news data to insert.")
        return None