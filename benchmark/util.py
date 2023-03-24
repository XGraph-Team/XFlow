def combinations(alist):
  n = len(alist)
  subs = [[]]

  for item in alist:
    subs += [curr + [item] for curr in subs]
  subs.sort(key=len)
  return subs

def subcombs(alist):
  subs = combinations(alist)
  subs.remove([])
  subs.remove(alist)
  subs.sort(key=len)
  return subs

def substract(alist, blist):
  a = []
  for i in alist:
    a.append(i)
  for i in blist:
    a.remove(i)
  return a

def diff(rank, order):
    n = len(rank)
    if (len(order) != n):
      print('the lengths do not match')
      pass
    else:
      difference = 0
      for i in range(n):
        item = rank[i]
        index = order.index(item)
        delta = abs(index - i)
        difference += delta
    return difference
