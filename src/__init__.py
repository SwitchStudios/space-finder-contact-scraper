import csv
import json
import requests
from bs4 import BeautifulSoup

baseUrl = 'https://dc.spacefinder.org'
url = baseUrl + '/spaces.html?page=1'
completeSpaceList = []

while url:
    print(url)
    response = requests.get(url)
    status = response.status_code

    if status != 200:
        print('Request error: {}'.format(status))

    else:
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        spaces = soup.find_all('div', class_='detail')
        print('This page contains {} results.'.format(len(spaces)))

        for s in spaces:
            spaceUrl = baseUrl + s.find('a')['href']
            spaceResponse = requests.get(spaceUrl)
            spaceHtml = spaceResponse.content
            bs = BeautifulSoup(spaceHtml, 'html.parser')
            name = bs.find('h1').string
            contactInfo = bs.find_all('span', class_='info_pair')
            if len(contactInfo) < 5:
                website = 'ERROR'
                person = 'ERROR'
                phone = 'ERROR'
                email = 'ERROR'
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
            space = {
                "Space Name": name,
                "Website": website,
                "Contact": person,
                "Phone": phone,
                "Email": email,
            }
            completeSpaceList.append(space)

        nextPage = soup.find(class_='next_page')
        if 'disabled' not in nextPage.attrs['class']:
            url = baseUrl + nextPage['href']
        else:
            url = ''

completeSpaceData = {
    "spaces": completeSpaceList
}
dump = json.dumps(completeSpaceData)
spaceListParsed = json.loads(dump)
spaceData = spaceListParsed['spaces']

# open a file for writing
spaceDataCsv = open('/Users/i851870/Code/personal/hoppispace/SpaceFinderDCContactList.csv', 'w')

# create the csv writer object
csvwriter = csv.writer(spaceDataCsv)

count = 0
for space in spaceData:
    if count == 0:
        header = space.keys()
        csvwriter.writerow(header)
        count += 1

    csvwriter.writerow(space.values())

spaceDataCsv.close()
