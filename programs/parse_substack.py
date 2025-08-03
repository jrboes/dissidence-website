import requests
import slugify
import xml.etree.ElementTree as ET
import bs4
import datetime
import html
import re



native_template = """
<div class="captioned-button-wrap">
 <div class="preamble">
  <p class="cta-caption">
   This Video is only available on Substack.
  </p>
 </div>
 <p class="button-wrapper">
  <a class="button primary" href="[LINK]">
   <span>Watch Now</span>
  </a>
 </p>
</div>
"""


url = 'https://jacobboes.substack.com/feed'
feed = requests.get(url)
xml = feed.text

tree = ET.ElementTree(ET.fromstring(xml))
root = tree.getroot()

namespaces = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

for item in root.iterfind('.//item'):
    creator = item.find('dc:creator', namespaces)
    if creator is None:
        continue
    creator = creator.text

    title = html.unescape(item.find('title').text)
    slug = slugify.slugify(title, max_length=30)
    link = html.unescape(item.find('link').text)

    pubDate = item.find('pubDate').text
    format = '%a, %d %b %Y %H:%M:%S %Z'
    date = datetime.datetime.strptime(pubDate, format)
    fmtDate = date.strftime('%Y-%m-%d-%H%M')
    image = item.find('enclosure').attrib['url']
    header = f"""---
title: "{title}"
date: "{date.isoformat()}"
author: "{creator}"
image: "{image}"
---
"""
    content = item.find('content:encoded', namespaces)
    if content is not None and content.text:
        soup = bs4.BeautifulSoup(content.text, features="html.parser")

        # Embedded native video handling
        native_div = soup.find_all('div', {'class': 'native-video-embed'})
        for el in native_div:
            native_template = native_template.replace('[LINK]', link)
            replacement = bs4.NavigableString(native_template)
            el.replace_with(replacement)

        # Embedded image handling
        image_div = soup.find_all('div', {'class': 'captioned-image-container'})
        for el in image_div:

            a_tag = el.find('a', class_='image-link')
            href_value = a_tag['href']

            replacement = bs4.NavigableString(f'<p> <img src="{href_value}" </p>')
            el.replace_with(replacement)

        # Embedded Youtube video handling
        image_extras = soup.find_all('div', {'class': 'youtube-wrap'})
        for el in image_extras:

            attr_string = el.attrs.get('data-attrs')
            match = re.search(r'"videoId":"(.*?)"', attr_string)
            video_id = match.group(1)

            replacement = bs4.NavigableString(f'{{{{< youtube {video_id} >}}}}')
            el.replace_with(replacement)

        body = soup.prettify(formatter=None).rstrip()
        with open(f'../content/articles/{fmtDate}-{slug}.md', 'w') as f:
            f.write(header + body)

