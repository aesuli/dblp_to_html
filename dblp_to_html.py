import re
import sys

import bs4
import requests


def render(content):
    soup = bs4.BeautifulSoup(content, features='xml')

    with open('biblio.html', mode='wt', encoding='utf-8') as outputfile:
        person = soup.find('person')
        print(f"<html><head><meta charset=\"UTF-8\"><link rel=\"stylesheet\" href=\"biblio.css\"/></head><body>",
              file=outputfile)
        print(f"<div class=\"biblio\"><div class=\"author\">{person.find('author').text}</div>", file=outputfile)
        print('<div class="pub_list">', file=outputfile)
        prev_year = None
        year = None
        for paper in soup.find_all('r'):
            year = paper.find('year').text
            if year != prev_year:
                if prev_year:
                    print('</div>', file=outputfile)
                print(f"<div class=\"year_block\"><div class=\"year_block_head\">{year}</div>", file=outputfile)
                prev_year = year
            pub_type = None
            if paper.find('inproceedings'):
                pub_type = 'inconf'
            elif paper.find('incollection'):
                pub_type = 'inbook'
            elif paper.find('article'):
                try:
                    if paper.next.attrs['publtype'] == 'informal':
                        pub_type = 'other'
                except KeyError:
                    pub_type = 'injour'
            elif paper.find('phdthesis'):
                pub_type = 'thesis'
            else:
                raise Exception(f"Unsupported publication type for {paper}")

            print(f"<div class=\"pub {pub_type}\">", file=outputfile)
            print(
                f"<div class=\"authors\">{', '.join([re.sub('[0-9]+', '', author.text).strip() for author in paper.find_all('author')])}.</div>",
                file=outputfile)
            urls = paper.find_all('ee')
            doi = None
            if urls:
                print(f"<div class=\"title\"><a href=\"{urls[0].text}\">{paper.find('title').text}</a></div>",
                      file=outputfile)
                for url in urls:
                    matches = re.findall('doi\.org/([^\s]+)', url.text)
                    if len(matches) > 0:
                        doi = matches[0]
                        break
            else:
                print(f"<div class=\"title\">{paper.find('title').text}</div>", file=outputfile)
            if pub_type == 'thesis':
                print(f"<div class=\"where\">{paper.find('school').text}</div>", file=outputfile)
            if pub_type == 'inconf' or pub_type == 'inbook':
                print(f"<div class=\"where\">{paper.find('booktitle').text}</div>", file=outputfile)
            if pub_type == 'injour' or pub_type == 'other':
                print(f"<div class=\"where\">{paper.find('journal').text}</div>", file=outputfile)
                print(f"<div class=\"volume\">{paper.find('volume').text}", end='', file=outputfile)
                if paper.find('number'):
                    print(f"({paper.find('number').text})</div>", file=outputfile)
                else:
                    print('</div>', file=outputfile)
            print(f"<div class=\"pages\">{year}</div>", file=outputfile)
            if paper.find('pages'):
                print(f"<div class=\"pages\">{paper.find('pages').text}</div>", file=outputfile)
            if doi:
                print(f"<div class=\"doi\"><a href=\"https://doi.org/{doi}\">{doi}</a></div>", file=outputfile)
            print('</div>', file=outputfile)
        if year:
            print('</div>', file=outputfile)
        print('</div>', file=outputfile)
        print('</div>', file=outputfile)
        print('</body></html>', file=outputfile)


if __name__ == '__main__':

    author_pid = '74/4209'
    if len(sys.argv) > 1:
        author_pid = sys.argv[-1]

    url = f'https://dblp.uni-trier.de/pid/{author_pid}.xml'

    content = requests.get(url).content.decode()
    render(content)
