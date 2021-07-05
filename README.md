# IR-evaluator

A tiny server-client evaluator for IR homework (e.g. Search Engine) in Python.

Teachers (or TAs) prepare <url, query> to evaluate students' search engines.

Students develop `search_engine.evaluate` to accept query, and return list of retrieved urls.

**MRR@20**, in defaults.

## Requirements

```
requests==2.25.1
flask==1.1.2
tqdm==4.61.1
```

## Quick Start

### File Preparation

```
ans.tsv             # evaluation cases, url<\t>query
example-ans.tsv     # no overlap with ans.tsv
passwd              # each line a password
archive/            # dir for saving clients' summited urls
```

### Server

```bash
python server.py
```

Retrieved urls will be saved into `archive/`, named as each student's `idx`.

`normal.log` for final submission logs, `debug.log` for debug mode logs, `illegal.log` for illegal operation logs.

### Client

Replace line 9 of `client.py` to your server's IP address.

```bash
python client.py
```

Enter `passwd` for the **final** submission (`ans.tsv` will be evaluated), while not enter `passwd` for the DEBUG mode (`example-ans.tsv` will be evaluated).

### Leaderboard

`localhost:8080/board` for a simple leaderboard
