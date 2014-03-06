# Manually generate combos first:
#
#   sqlite> .output combos.txt
#   sqlite> select food_id, attribute_id from food_attribute_filtered2 order by food_id, attribute_id;
#
# Then run this for the counts

from collections import defaultdict

counts = defaultdict(lambda: 0)
current_id = 1
current_key = set()
with open('combos.txt') as f:
    for line in f:
        new_id, num = line[:-1].split('|')
        if new_id != current_id:
            current_key = frozenset(current_key)
            counts[current_key] += 1
            current_id = new_id
            current_key = set()

        current_key.add(num)

sets = [k for k in counts.keys() if counts[k] > 1] # exclude count=1 cases
#counts = [counts[k] for k in sets]

attributes = set()
for s in sets:
    attributes = attributes.union(s)
attributes = sorted(list(attributes))

sets_by_attribute = {}
for attribute in attributes:
    sets_by_attribute[attribute] = [i for i, s in enumerate(sets) if attribute in s]

print(len(sets))

def fill(s1, count, sets, sets_by_attribute):
    #sets_by_attribute.sort(key=lambda x: len(x))
    sum_ = 0
    sets_by_attribute
    for i, s2 in enumerate(sets):
        s = s1.union(s2)
        if s == s1:
            continue
        if count > 2**30 or sum_ > 2**30:
            print(count)
            print(sum_)
            os.exit()
        sum_ += fill(s, count * counts[s2], sets[i+1:], sets_by_attribute)
    return sum_

print(fill(set(), 1, sets, sets_by_attribute))
