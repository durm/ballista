# -*-coding:utf-8-*-

from flask import Flask, request, render_template, abort
import random
import copy

app = Flask(__name__)


def accumulate(x, y):
    banners = set()
    if y in categories2banners:
        banners = categories2banners[y]
    return x | banners


@app.route("/")
def banner():
    categorylist = request.args.getlist("category[]")[:10]
    if  not categorylist:
        choises = banners2categories.keys()
    else:
        choises = reduce(accumulate, categorylist, set())
    if not choises:
        abort(404)
    banner = random.choice(list(choises))
    dec_shows(banner)
    return render_template("banner.html", banner=banner)


@app.route("/stats/<t>/")
def stats(t):
    data = None
    if t == "banners2shows":
        data = copy.copy(banners2shows)
    elif t == "banners2categories":
        data = copy.copy(banners2categories)
    elif t == "categories2banners":
        data = copy.copy(categories2banners)
    else:
        abort(404)
    return render_template("stats.html", data=data, t=t)


def dec_shows(banner):
    shows = banners2shows[banner] - 1
    banners2shows[banner] = shows
    if shows == 0:
        del banners2shows[banner]
        for category in banners2categories[banner]:
            categories = categories2banners[category]
            categories.remove(banner)
            if not categories:
                del categories2banners[category]
        del banners2categories[banner]


def parse_conf(fpath, banners2shows, categories2banners, banners2categories):
    with open(fpath) as f:
        for item in f:
            item = item.split(";")
            banner = item[0]
            shows = int(item[1])
            categories = map(lambda x: x.strip(), item[2:])
            banners2shows[banner] = shows
            banners2categories[banner] = set(categories)
            for category in categories:
                if category not in categories2banners:
                    categories2banners[category] = set()
                categories2banners[category].add(banner)

if __name__ == "__main__":
    import sys
    banners2shows = {}
    categories2banners = {}
    banners2categories = {}
    fpath = sys.argv[1]
    parse_conf(fpath, banners2shows, categories2banners, banners2categories)
    app.debug = True
    app.run(host="0.0.0.0")
