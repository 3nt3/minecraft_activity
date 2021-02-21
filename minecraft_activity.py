# from matplotlib import pyplot as plt
import gzip
import os
import re
import datetime
import time
from matplotlib import pyplot as plt

files = os.listdir()
log_zip_files = []

logs = ""

# fn for file name
for fn in os.listdir():
    if fn.endswith(".log"):
        with open(fn) as f:
            logs += f"\n<<<{datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')}>>>\n" + \
                f.read() + '\n'

    elif fn.endswith(".log.gz"):
        log_zip_files.append(fn)

for fn in log_zip_files:
    with gzip.open(fn) as f:
        logs += f"\n<<<{fn[:10]}>>>\n" + f.read().decode('utf-8') + '\n'

lines = logs.split('\n')

r_date = re.compile(r'^\[..:..:..\]')
r_brackets = re.compile(r'[\[,\]]')


def parse_line(line, current_date):
    data = {}

    match = r_date.search(line)
    if match:
        data["date"] = current_date + " " + \
            re.sub(r_brackets, '', match.group(0))

    match = re.search(r'logged', line)
    if match:
        data["login"] = True
        data["player_name"] = re.sub(r'\[(.*)\]', '', line.split(' ')[3])

    match = re.search(r'left the game', line)
    if match:
        data["login"] = False
        data["player_name"] = line.split(' ')[3]

    return data


player_data = {}

current_date = None
for line in lines:
    if re.search(r'^<<<[0-9]{0,4}-[0-9]{0,2}-[0-9]{0,2}>>>$', line):
        current_date = re.sub(r'[<>\n]', '',  line)

    parsed = parse_line(line, current_date=current_date)
    if parsed.get("login") is not None:
        if parsed["login"] == True:
            if player_data.get(parsed["player_name"]):
                if player_data[parsed["player_name"]][-1][0] == None and player_data[parsed["player_name"]][-1][1] is not None:
                    player_data[parsed["player_name"]][-1][0] = parsed["date"]
                else:
                    player_data[parsed["player_name"]].append(
                        [parsed["date"], None])
            else:
                player_data[parsed["player_name"]] = [[parsed["date"], None]]

        if parsed["login"] == False:
            if player_data.get(parsed["player_name"]):
                if player_data[parsed["player_name"]][-1][1] == None and player_data[parsed["player_name"]][-1][0] is not None:
                    player_data[parsed["player_name"]][-1][1] = parsed["date"]
                else:
                    player_data[parsed["player_name"]].append([
                        None, parsed["date"]])
            else:
                player_data[parsed["player_name"]] = [[None, parsed["date"]]]

player_colors = {}

i = 0
for player_name in player_data.keys():
    for entry in player_data[player_name]:
        if entry[0] is None or entry[1] is None:
            print("incomplete entry")
            continue

        entry[0] = time.mktime(datetime.datetime.strptime(
            entry[0], "%Y-%m-%d %H:%M:%S").timetuple())

        entry[1] = time.mktime(datetime.datetime.strptime(
            entry[1], "%Y-%m-%d %H:%M:%S").timetuple())

        # plot
        if not player_colors.get(player_name):
            lines = plt.plot(entry, [i, i], linewidth=5,
                             solid_capstyle='round', label=player_name, marker='x', markersize=10, markeredgecolor='black')
            player_colors[player_name] = lines[0].get_color()
            plt.legend()

        else:
            plt.plot(entry, [i, i], linewidth=5,
                     solid_capstyle='round', color=player_colors[player_name], marker='x', markersize=10, markeredgecolor='black')

    i += 1


plt.show()
