import random
import re

import matplotlib.pyplot as plt

# 2593

data = open("logs/samples.log", "r").readlines()
output = []
parallel = []  # To find out the postion of a score in the "data" variable since it doesn't directly translate
for i, datum in enumerate(data):
    temp = re.findall("SCORE: ([0-9]*)", datum)
    if len(temp) > 0 and temp[0].isnumeric():
        output.append(int(temp[0]))
        parallel.append(i)

averages = []
total = 0
for i, out in enumerate(output):
    total += out
    averages.append(total / (i + 1))

running_averages = []
totals = []
for i, out in enumerate(output):
    totals.append(out)
    if len(totals) > 100:
        totals.pop(0)
    running_averages.append(sum(totals) / len(totals))

plt.subplot(1, 3, 1)
plt.scatter(range(len(output)), output)
plt.subplot(1, 3, 2)
plt.scatter(range(len(averages)), averages)
plt.subplot(1, 3, 3)
plt.scatter(range(len(running_averages)), running_averages)

plt.tight_layout()
plt.show()
