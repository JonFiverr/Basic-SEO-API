from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from requests.exceptions import ConnectTimeout, TooManyRedirects, Timeout
import nltk
from nltk.tokenize import word_tokenize


class Optimizer:

  def __init__(self):
    nltk.download('stopwords')
    nltk.download('punkt')
    self.url = ''

  def update_url(self, url):
    self.url = url
    print(self.url)

  def page_check(self):
    keywords = []
    try:
      res = requests.get(self.url).text
    except (ConnectTimeout, TooManyRedirects, TimeoutError, Timeout):
      res = False

    if res:
      soup = BeautifulSoup(res, 'html.parser')

      # Title
      title = self.get_title(soup)

      # Meta
      meta = self.get_meta(soup)

      # Headers
      head = self.get_headings(soup)

      # Internal Links
      in_links, out_links = self.get_page_links(self.url, soup)
      # Both have e.g in_links['count'] and in_links['page_in_links']
      # for i in in_links['page_in_links']:
      #     print(f"{i['text']} -> {i['link']}")

      # for i in out_links['page_out_links']:
      #     print(f"{i['text']} -> {i['link']}")

      # Image ALT Text
      alt_text = self.get_alt_text(soup)

      # Keywords
      keywords = self.get_keyword_data(soup)

      return {
        'title': title,
        'meta': meta,
        'head': head,
        'links': {
          'in-links': in_links,
          'out-links': out_links
        },
        'alt-text': alt_text,
        'keywords': keywords
      }

  def get_keyword_data(self, soup):
    body = soup.find('body').text
    words = [i.lower() for i in word_tokenize(body)]
    sw = nltk.corpus.stopwords.words('english')
    nwords = []
    for i in words:
      if i not in sw and i.isalpha():
        nwords.append(i)

    # 15 most common as a list
    freq = nltk.FreqDist(nwords).most_common(20)

    kw = []
    for i in freq:
      kw.append({'word': str(i[0]), 'count': int(i[1])})

    return kw

  def get_title(self, soup):
    info = []
    # Title
    title = soup.find('title').text
    if title:
      info.append({'has_title': True})
      info.append({'title': str(title)})
      if len(title) < 50 or len(title) > 70:
        info.append({
          'title_length':
          f'Title should be between 50-70 characters, current title is {len(title)} characters.'
        })
      else:
        info.append({
          'title_length':
          'Title length is between 50 and 70 characters. Good Job!'
        })
    else:
      info.append({'has_title': False})
      info.append({'title': 'None'})
      info.append({'title_length': 'Title Is Missing!!!'})
    return info

  def get_meta(self, soup):
    info = []
    # Meta Description
    meta_content = ''
    meta_desc = soup.findAll('meta', attrs={'name': 'description'})
    for item in meta_desc:
      meta_content += f'{item["content"]}\n'
    meta_content = meta_content[:-1]

    if meta_content != '':
      info.append({'has_meta': True})
      info.append({'meta': str(meta_content)})
      if len(meta_content) < 150 or len(meta_content) > 160:
        info.append({'meta_len': str(len(meta_content))})
      else:
        info.append({'meta_len': str(len(meta_content))})
    else:
      info.append({'has_meta': False})
      info.append({'meta': "None"})
      info.append({'meta_len': '0'})

  def get_headings(self, soup):
    hs = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    h1, h2, h3, h4, h5, h6 = 0, 0, 0, 0, 0, 0
    hone = []
    htwo = []
    hthree = []
    hfour = []
    hfive = []
    hsix = []

    for h in soup.find_all(hs):
      if h.name == 'h1':
        h1 += 1
        hone.append(h.text)
      elif h.name == 'h2':
        h2 += 1
        htwo.append(h.text)
      elif h.name == 'h3':
        h3 += 1
        hthree.append(h.text)
      elif h.name == 'h4':
        h4 += 1
        hfour.append(h.text)
      elif h.name == 'h5':
        h5 += 1
        hfive.append(h.text)
      elif h.name == 'h6':
        h6 += 1
        hsix.append(h.text)

    headings = {
      'h1': {
        'count': h1,
        'text': hone
      },
      'h2': {
        'count': h2,
        'text': htwo
      },
      'h3': {
        'count': h3,
        'text': hthree
      },
      'h4': {
        'count': h4,
        'text': hfour
      },
      'h5': {
        'count': h5,
        'text': hfive
      },
      'h6': {
        'count': h6,
        'text': hsix
      }
    }
    return headings

  def get_page_links(self, url, soup):
    parsed = urlparse(url)
    domain = f'{parsed.netloc}'

    in_l = []
    out_l = []

    for link in soup.find_all('a'):
      try:
        href = link.get('href')
        if href.startswith('/'):
          # Internal Link
          in_l.append({
            'text': link.text,
            'link': f'{parsed.schema}://{domain}{i}'
          })
        elif domain in href:
          # Internal Link
          in_l.append({'text': link.text, 'link': href})
        elif domain not in href and not href.startswith('#'):
          # External Link
          out_l.append({'text': link.text, 'link': href})
      except:
        continue

    in_links = {'count': len(in_l), 'page_in_links': in_l}
    out_links = {'count': len(out_l), 'page_out_links': out_l}

    return in_links, out_links

  def get_alt_text(self, soup):
    imgs = []
    for i in soup.find_all('img', alt=False):
      imgs.append({'image': i, 'alt': 'This image has no ALT text!'})
    for i in soup.find_all('img', alt=True):
      imgs.append({'image': i, 'alt': i['alt']})

    return imgs
