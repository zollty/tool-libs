from bs4 import BeautifulSoup

with open(r'D:\__SYNC2\git\zollty-misc\tool-libs\Python\zollty_tools\test_clean.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

spans = soup.find_all('span')
print(f'Found {len(spans)} span tags')
for span in spans:
    span.unwrap()

with open(r'D:\__SYNC2\git\zollty-misc\tool-libs\Python\zollty_tools\test_clean.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print('Done')
