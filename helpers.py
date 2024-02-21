from dataclasses import dataclass
from typing import IO, List
from requests import get
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

CRAIGSLIST_URL = "https://vancouver.craigslist.org/search/apa?max_price=1800#search=1~gallery~0~0"

@dataclass
class Listing:
    """
    Describes one Craiglist listing.
    """
    title: str
    price: int
    location: str
    link: str

def format_string(s:str) -> str:
    """
    Formats a string to simplify filtering and validation.

    Arguments:
        s: the string to be formatted
    Returns:
        a lowercase string with any alphanumeric or whitespace characters removed.
    """
    line = s.lower()
    line = "".join(line.strip())
    pattern = r'[^a-zA-Z0-9\s]'
    line = re.sub(pattern, '', line)
    return line

def make_int(num: str) -> int:
    """
    Used to format price strings.

    Arguments:
        num: the string representation of an integer number
    Returns:
        an integer that has all non-numeric characters removed.
    """
    chars = ['$', ',']
    for old in chars:
        num = num.replace(old, "")
    n = int(num)
    return num

def get_data() -> List[Listing]:

    r = get(CRAIGSLIST_URL)
    s = BeautifulSoup(r.text, 'html.parser')

    title = [format_string(k.text) for k in s.find_all('div', class_='title')]
    price = [make_int(k.text) for k in s.find_all('div', class_='price')]
    locations = [format_string(k.text) for k in s.find_all('div', class_='location')]
    link = [k.get('href') for k in s.find_all('a')]
    listings = []
    for i in range(len(title)):
        listings.append(Listing(title[i], price[i], locations[i], link[i]))
    return listings



def filter_cities(all_listings: List[Listing] = get_data()) -> List[Listing]:
    """
    Removes all listings that are located in cities not of interest.

    Arguments: 
        all_listings: the list of Listing objects to filter.
    Returns:
        a list of Listing objects, with titles, locations, and links checked to ensure that 
        only desirable locations are returned
    """

    # the list of cities to filter out
    to_filter = ['surrey', 'delta', 'port', 'westminster', 'burnaby', 'mission', 'cloverdale', 'abbotsford', 'langley', 'coquitlam']

    # checks for any substrings in Listing objects that match the above list.
    filtered_locations = [l for l in all_listings if not any(f in l.location for f in to_filter)]
    filtered_links = [l for l in filtered_locations if not any(f in l.link for f in to_filter)]
    filtered_titles = [l for l in filtered_links if not any(f in l.title for f in to_filter)]
    return filtered_titles


def write_to_file(output_dir: str = "output") -> IO:
    """
    Writes the output after applying the filter to a .txt file.

    Arguments:
        output_dir: optional string to specify where results should be saved. Defaults to creating a new
                    directory in the cwd called "output".
    Returns:
        a text file with matching listings.
    """
    filtered_data = filter_cities()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_datetime = datetime.now().strftime("%H-%M-%S_%Y-%m-%d")
    file_name = f"{current_datetime}_available_listings.txt"

    f = os.path.join(output_dir, file_name)

    # Write filtered listings to the file
    with open(f, "w") as file:
        for listing in filtered_data:
            file.write(f"Title: {listing.title}\n"
                       f"Location: {listing.location}\n"
                       f"Price: ${listing.price}\n"
                       f"Link: {listing.link}\n"
                       "\n")
    
    print(f'{len(filtered_data)} entries written to {file_name}')
    return f