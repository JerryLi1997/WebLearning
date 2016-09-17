import io
import sys
import os
import requests
from bs4 import BeautifulSoup, Comment
from contextlib import closing
totalpath = 'F:/Lessons'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
headers = {'Host': 'learn.tsinghua.edu.cn', 'Referer': 'http://learn.tsinghua.edu.cn', 'Oringin': 'http://learn.tsinghua.edu.cn',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Connection': 'keep-alive'}
s = requests.Session()

s.post("https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp",
       {'userid': , 'userpass': , 'submit1': '登录'}, headers=headers)
r = s.get(
    "http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?language=cn")
content = r.content.decode('utf8')
soup = BeautifulSoup(content, 'lxml')
commoncourse = {}
specialcourse = {}
for child in soup.find_all('a'):
    if 'course_id' in child['href']:
        split1 = child.text.strip().split('(')
        split2 = child['href'].split('course_id=')
        commoncourse[split2[1]] = split1[0]
    elif 'coursehome' in child['href']:
        split1 = child.text.strip().split()
        split2 = child['href'].split('coursehome/')
        specialcourse[split2[1]] = split1[0]


def downloadfile(url, coursename, filename):
    coursepath = os.path.join(totalpath, coursename)
    if not os.path.exists(coursepath):
        os.mkdir(coursepath)
    filepath = os.path.join(coursepath, filename)
    with closing(s.get(url, stream=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 内容体总大小
        progress = ProgressBar(filepath, total=content_size,
                               unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
        with open(filepath, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                progress.refresh(count=len(data))


class ProgressBar(object):

    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "【%s】%s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status,
                             self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


def downloadcommoncourse(key):
    coursefile = {}
    coursedownloadhtml = s.get(
        'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id=' + key)
    coursesoup = BeautifulSoup(
        coursedownloadhtml.content.decode('utf8'), 'lxml')
    comments = coursesoup.findAll(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        split1 = (comment.split('&id')[0]).split('link=')[1]
        split2 = comment.split('",')[1].split('"')[1]
        coursefile[split2] = split1
    for child in coursesoup.find_all('a'):
        if 'uploadFile' in child['href']:
            downloadfile('http://learn.tsinghua.edu.cn/' +
                         child['href'], commoncourse[key], coursefile[child['href'].split('file_id=')[1].split('"')[0]])

for course in commoncourse:
	downloadcommoncourse(course)
