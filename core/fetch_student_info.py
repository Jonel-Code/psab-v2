import mechanicalsoup
from lxml.html import fromstring
from bs4 import BeautifulSoup
import requests
from random import choice

# user agents from: https://developers.whatismybrowser.com/useragents/explore/
user_agents = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.29 Safari/537.36',
    'Mozilla/5.0 (Linux; NetCast; U) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.31 SmartTV/6.0',
    'Mozilla/5.0 (Linux; NetCast; U) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.33 Safari/537.31 SmartTV/5.0',
    'Mozilla/5.0 (SMART-TV; LINUX; Tizen 3.0) AppleWebKit/538.1 (KHTML, like Gecko) Version/3.0 TV Safari/538.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/57.0.2987.98 Chrome/57.0.2987.98 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
]


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


proxies = list(get_proxies())
print('proxies:', proxies)


def get_student_info(username: str, password: str):
    # use of mechanicalsoup for getting a session id after logging in
    # then use it on request as item on cookies
    base_url = 'http://student.plmun.edu.ph/'
    grades_portal = base_url + 'grades.php'

    login_form_id = '#login'
    input_username_name = 'studentnumber'
    input_password_name = 'password'
    _proxy = choice(proxies)
    print('_proxy:', _proxy)

    br = mechanicalsoup.StatefulBrowser()
    br.session.proxies = _proxy
    # login using the base url since it will be automatically redirects the browser to login page
    br.open(base_url)

    # select the login form and fill up the contents of the form using the login info
    br.select_form(login_form_id)
    br[input_username_name] = username
    br[input_password_name] = password
    # submit the login information
    br.submit_selected()

    # setup headers
    headers = {
        'User-Agent': choice(user_agents)
    }

    # store cookies recived from mechanicalsoup as cookies for the next request that requires session cookies
    cookies_dict = br.get_cookiejar()
    print('cookies', br.get_cookiejar()['PHPSESSID'])

    # start request session
    with requests.Session() as reqs:
        rq = reqs.get(grades_portal, proxies={"http": _proxy, "https": _proxy}, headers=headers, cookies=cookies_dict)
        print('headers:', rq.request.headers)
        soup = BeautifulSoup(rq.text, "html.parser")

        grades_soup = soup.find_all('table', 'table table-stripes')
        print('type of grades_soup:', type(grades_soup))

        grades_str = ''
        tbl_header_str = ''
        tbl_header_soup = grades_soup[1].find_all('th')

        for i, item in enumerate(tbl_header_soup):
            td_excluded = [1, len(tbl_header_soup) - 1]
            if i not in td_excluded:
                tbl_header_str += f'\n{item.contents}'
        print('tbl_header:', tbl_header_str)
        for item in grades_soup:
            all_rows = item.find_all('tr')
            for res in all_rows[1:len(all_rows) - 2]:
                all_td = res.find_all('td')
                td_excluded = [1, len(all_td) - 1]
                for i, td in enumerate(all_td):
                    if i not in td_excluded:
                        grades_str = f'{grades_str}\n {str(td.contents)}'

        print(grades_str)
        return grades_str
    # end request session

#
# def determine_curriculum(student_id: str, course: str):
#     from app import get_curriculum
#     entry_year = "20" + str(student_id[0:2]) + str(int(student_id[0:2]) + 1)
#     print('entry_year', entry_year)
#     curriculum_course = get_curriculum()[course.upper()]
#     if curriculum_course is not None:
#         curriculum_years = [int(key) for key in curriculum_course.keys() if int(key) <= int(entry_year)]
#         # return latest curriculum if the entry year is too old and not available in database
#         return str(max(curriculum_years)) if len(curriculum_years) > 0 else str(max(curriculum_course))
#     return None
#
#
# def get_curriculum_subjects(course: str, curriculum_year: str):
#     from app import get_curriculum
#     return get_curriculum()[course.upper()][curriculum_year]['subjects']
#

if __name__ == '__main__':
    get_student_info('16118081', 'a123654')
