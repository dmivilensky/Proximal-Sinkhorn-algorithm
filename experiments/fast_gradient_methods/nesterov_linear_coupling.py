# -*- coding: utf-8 -*-
"""Linear Coupling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UlWUQtvr7dRH_uusgAEThGHZT_zvPgVs
"""

import numpy as np
import copy

def task(x):
    return sum([(i + 1) * (x[i] ** 2) for i in range(len(x))])

def task_gradient(x):
    return np.array([(i + 1) * x[i] * 2 for i in range(len(x))])

def find_r(y):
    x = 0
    j = 2
    px = 0
    while 1:
        x = j
        j *= 2
        if task(y - px * task_gradient(y)) <= task(y - x * task_gradient(y)):
            break
        px = x
    return x

def ternary_search_beta(eps, l, r, u, x):
    while(r - l > eps):
        m1 = l + (r - l) / 3
        m2 = r - (r - l) / 3
        if(task(u + m1 * (x - u)) < task(u + m2 * (x - u))):
            r = m2
        else:
            l = m1
    return r
def ternary_search_h(eps, l, r, y):
    while(r - l > eps):
        m1 = l + (r - l) / 3
        m2 = r - (r - l) / 3
        if(task(y - m1 * task_gradient(y)) < task(y - m2 * task_gradient(y))):
            r = m2
        else:
            l = m1
    return r

def linear_coupling(x, eps):
  n = len(x)
  alphprev = 0
  L = 2 * n
  xres = np.zeros(n)
  xprev = x
  uprev = xprev[:]
  k = 0
#   bcur = np.array([i / (i + 2) for i in range(n)])
#   hcur = np.array([1 / L for i in range(n)])
  Acur = 0
  while(1):
      bcur = ternary_search_beta(eps, 0, 1, uprev, xprev)
      ycur = uprev + bcur * (xprev - uprev)
      r = find_r(ycur)
      hcur = ternary_search_h(eps, 0, r, ycur)
      xcur = ycur - hcur * task_gradient(ycur)
      Acur += alphprev
      alphcur = ((task(ycur) - task(xcur)) + np.sqrt((task(ycur) - task(xcur)) * ((task(ycur) - task(xcur)) + 2 * Acur * np.linalg.norm(task_gradient(ycur)) ** 2)) )/ (np.linalg.norm(task_gradient(ycur)) ** 2)
      ucur = uprev - alphcur * task_gradient(ycur)
      # Here break criteria
      if(task(xprev) - task(xres) <= eps):
        break
      xprev = xcur
      uprev = ucur
      alphprev = alphcur
      k += 1
  return xprev, k

x = np.array([i for i in range(100, 0, -1)])
print(linear_coupling(x, 0.001))
