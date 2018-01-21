import csv
import json
import requests
from bs4 import BeautifulSoup

##
# STEP 1: Scrape SpaceFinderDC for space contact data
##

baseUrl = 'https://dc.spacefinder.org'
url = baseUrl + '/spaces.html?page=1'
completeSpaceList = []

# While there is a valid Next Page link, continue to next page of results
while url:
    print(url)
    response = requests.get(url)
    status = response.status_code

    if status != 200:
        print('Request error: {}'.format(status))

    # Successful 200 response from SpaceFinder.org
    else:
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        spaces = soup.find_all('div', class_='detail')
        print('This page contains {} results.'.format(len(spaces)))

        # For each space in search results list, navigate to it's detailed view and parse
        for s in spaces:
            # Get the space details url and setup with BeautifulSoup for html parsing
            spaceUrl = baseUrl + s.find('a')['href']
            spaceResponse = requests.get(spaceUrl)
            spaceHtml = spaceResponse.content
            bs = BeautifulSoup(spaceHtml, 'html.parser')

            name = bs.find('h1').string
            contactInfo = bs.find_all('span', class_='info_pair')

            # This is a hack because the SpaceFinder site blows and html structure varies slightly on some pages
            # * insert massive eye roll emoji here *
            # Any rows in the final csv with ERROR or unexpected data, please verify manually
            if len(contactInfo) < 5:
                website = 'ERROR'
                person = 'ERROR'
                phone = 'ERROR'
                email = 'ERROR'

            # Even if the contact info section has the expected number of elements, they could be in a bizarre order
            # This handles those cases to avoid exceptions.. sloppily I admit
            else:
                website = contactInfo[0].find('a')
                if website:
                    website = website['href']
                person = contactInfo[1]
                if person:
                    person = person.text[9::]
                phone = contactInfo[2].find(class_='not_mobile_only')
                if phone:
                    phone = phone.text
                email = contactInfo[3].find('a')
                if email:
                    email = email.text

            lastUpdated = bs.find('p', class_='subtle').text

            # Format the json object for our space and add to the main list
            space = {
                "Space Name": name,
                "Website": website,
                "Contact": person,
                "Phone": phone,
                "Email": email,
            }
            completeSpaceList.append(space)

        # Reset url and check for the url of the next page
        url = ''
        nextPage = soup.find(class_='next_page')
        if 'disabled' not in nextPage.attrs['class']:
            url = baseUrl + nextPage['href']

##
# STEP 2: Format and write scraped json list into CSV document
##

completeSpaceData = {
    "spaces": completeSpaceList
}
dump = json.dumps(completeSpaceData)
spaceListParsed = json.loads(dump)
spaceData = spaceListParsed['spaces']

# Open a file for writing
tempFile = '/Users/i851870/Code/personal/hoppispace/SpaceFinderDCContactList.csv'
spaceDataCsv = open(tempFile, 'w')

# Create the csv writer object
csvwriter = csv.writer(spaceDataCsv)

count = 0
for space in spaceData:
    if count == 0:
        header = space.keys()
        csvwriter.writerow(header)
        count += 1

    csvwriter.writerow(space.values())

# Close/save
spaceDataCsv.close()
