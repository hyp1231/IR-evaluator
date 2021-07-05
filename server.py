import os
import json
from datetime import datetime
import difflib
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

def curtime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(mode, msg):
    with open(f'{mode}.log', 'a', encoding='utf-8') as file:
        file.write(f'{curtime()}\t{mode}\t{msg}\n')

def load_passwd(filepath='passwd'):
    passwds = set()
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            passwds.add(line.strip())
    return passwds

passwds = load_passwd()

def load_ans(filepath='ans.tsv'):
    ans = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            ans.append(line.strip().split('\t'))
    return ans

ans = load_ans()
example_ans = load_ans('example-ans.tsv')

def get_content(url):
    r = requests.get(url)
    return r.url, r.text

def sim_text(text_a, text_b):
    ratio = difflib.SequenceMatcher(None, text_a, text_b).quick_ratio()
    return ratio > 0.9

def check(url_a, url_b):
    url_a, text_a = get_content(url_a)
    url_b, text_b = get_content(url_b)
    return url_a == url_b or sim_text(text_a, text_b)

def calcu_single_mrr(ans_url, pre_urls):
    for i, pre_url in enumerate(pre_urls):
        if i >= 20:
            break
        if check(ans_url, pre_url):
            return 1. / (i + 1)
    return 0.

def calcu_score(ans, pre):
    tot_mrr = 0
    for (ans_url, query), pre_urls in zip(ans, pre):
        tot_mrr += calcu_single_mrr(ans_url, pre_urls)
    return tot_mrr / len(ans)

@app.route('/login', methods=['POST'])
def login():
    idx = request.form['idx']
    passwd = request.form['passwd']

    if passwd == '':
        log('debug', f'{idx}\t{passwd}\tlogin')
        return str({'mode': 'debug', 'queries': list(zip(*example_ans))[1]})
    elif passwd in passwds:
        log('normal', f'{idx}\t{passwd}\tlogin')
        return str({'mode': 'normal', 'queries': list(zip(*ans))[1]})
    else:
        log('illegal', f'{idx}\t{passwd}\tlogin')
        return str({'mode': 'illegal', 'queries': ''})

@app.route('/mrr', methods=['POST'])
def mrr():
    idx = request.form['idx']
    passwd = request.form['passwd']
    urls = eval(request.form['urls'])

    if passwd == '':
        mrr = calcu_score(example_ans, urls)
        log('debug', f'{idx}\t{passwd}\t{mrr}\ttest')
        return str({'mode': 'debug', 'mrr': mrr})
    elif passwd in passwds:
        if os.path.exists(f'archive/{idx}'):
            log('illegal', f'{idx}\t{passwd}\ttwice_test')
            return str({'mode': 'normal', 'mrr': -1})
        else:
            with open(f'archive/{idx}', 'w', encoding='utf-8') as file:
                file.write(json.dumps(urls))
                mrr = calcu_score(ans, urls)
                log('normal', f'{idx}\t{passwd}\t{mrr}\ttest')
                return str({'mode': 'normal', 'mrr': mrr})
    else:
        log('illegal', f'{idx}\t{passwd}\ttest')
        return str({'mode': 'illegal', 'mrr': 0})

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/board')
def board():
    students = []

    with open('normal.log', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip().split('\t')
            if line[-1] == 'test':
                student = {
                    'idx': line[2],
                    'mrr': round(float(line[4]), 4),
                    'time': line[0],
                    'ta': line[3][:-1],
                    'class': line[3][-1]
                }
                students.append(student)

    students.sort(key=lambda t: t['mrr'], reverse=True)

    for i in range(len(students)):
        students[i]['mrr'] = str(students[i]['mrr'])

    return render_template('board.html', time_str=curtime(), students=students)

app.run(host='0.0.0.0', port=8080, debug=True)
