import datetime
from requests_html import HTMLSession
from .database import SessionLocal
from .crud import create_news
from .schemas import NewsCreate
from sqlalchemy.orm import Session

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
        # publisher_website = url.split('/')[2]
        # publisher = publisher_website.split('.')[-2]
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
            # publisher_website=publisher_website,
            # news_publisher=publisher,
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




def scrape_and_store_news(url: str, db: Session ):
    # db = SessionLocal()
    news_data = single_news_scraper(url)
    print(news_data)
    inserted_news = ""
    if news_data:
        # print(news_data)
        inserted_news = create_news(db=db, news=news_data)
    db.close()

    return inserted_news