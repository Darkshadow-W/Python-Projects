import requests
from bs4 import BeautifulSoup

def scrape_rentals(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This is a generic example; adjust selectors based on the actual website
        listings = soup.find_all('div', class_='listing')  # Example class
        for listing in listings:
            title = listing.find('h2').text if listing.find('h2') else 'No title'
            price = listing.find('span', class_='price').text if listing.find('span', class_='price') else 'No price'
            print(f"Title: {title}, Price: {price}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Enter rental website URL: ")
    scrape_rentals(url)