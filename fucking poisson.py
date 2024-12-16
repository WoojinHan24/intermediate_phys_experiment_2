#!/usr/bin/env python
# coding: utf-8

# In[154]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numba import jit
from scipy.integrate import quad
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import cauchy
from sklearn.metrics import r2_score


# In[2]:


fig, ax = plt.subplots(1, 1)


# In[80]:


observed_times = ["1136", "1137", "1138", "1139", "1140"]


# In[107]:


times = []
cummulative_number = []
last_time = 0
last_cummulative_number = 0

for ob_time in observed_times: 
    df = pd.read_excel("301_3floor_" + ob_time + "am.xlsx")
    df_times = np.subtract(list(df["time [s]"]), -last_time)
    last_time = df_times[len(df_times)-1]
    times = times + df_times
    
    df_cummulative_number = list(df["cummulative_number []"])
    
    
    cummulative_number.append(np.subtract(df_cummulative_number,-last_cummulative_number))
    last_cummulative_number = cummulative_number[len(cummulative_number)-1]
    
    
cummulative_number


# In[71]:


df = pd.read_excel("301_3floor_1128am.xlsx")

list(df["cummulative_number []"])


# In[124]:


len(muon_detected_time_distances)


# In[115]:


exp_times = ["1128am", "1136am", "1137am", "1138am", "1139am", "1140am"]
muon_detected_time_distances = []
for exp_time in exp_times:
    df = pd.read_excel(f"./301_3floor_{exp_time}.xlsx")
    times = list(df["time [s]"])
    muon_detected_time_distances.extend(np.array(times[1:]) - np.array(times[:-1]))

# print(muon_detected_time_distances)
plt.hist(muon_detected_time_distances)
plt.show()
len(muon_detected_time_distances)


# In[110]:


from scipy.stats import kstest, poisson


# In[134]:


ks_statistic, p_value = kstest(muon_detected_time_distances, 'exponential', args=(np.mean(muon_detected_time_distances),0))
print(ks_statistic, p_value)


# In[153]:


plt.hist(y, bins=100)
x = np.linspace(0,8.25,1000)
plt.plot(x,463*1/np.mean(muon_detected_time_distances)*np.exp((-1/np.mean(muon_detected_time_distances))*x), 'r--', label=r'$(\lambda =$' + str(muon_detected_time_distances) + ')')
plt.xlabel("detected time distances [s]")
plt.show("")


# In[133]:


popt, pcov = curve_fit(c*np.exp(-c*x), data.phase, data.output, p0=[0.01,180,0.6])
print(popt)
print(np.sqrt(pcov[1][1]))


# In[162]:






# In[180]:


b = 900

hist, bin_edges = np.histogram(muon_detected_time_distances, bins=b)
print(hist)
plt.hist(muon_detected_time_distances, bins=b)
len(hist)
time = bin_edges[:b]
count = hist

popt, pcov = curve_fit(exp_dis, time, hist)
print(popt)
print(pcov)
plt.hist(muon_detected_time_distances, bins=b)
plt.plot(time, exp_dis(time,popt), 'r--')


# In[160]:


def exp_dis(x,c):
    return c*np.exp(-c*x)

