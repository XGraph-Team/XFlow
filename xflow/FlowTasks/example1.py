from flow_tasks import forward, backward , graph_eval

# ### Testing / Examples

# a FW1 dataset, with the observations stored as attributes to a networkx graph

# In[20]:


fwd = forward(1, obs_storage = 'networkx')

print('Data points contain the values: ')
for key, value in fwd[0][0].items():
    print(f'{key}: {type(value)}, ', end='')
print()
print()

for ss_set in fwd:
    print('Snapshots at: ', sep='', end='')
    for ss in ss_set:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = ss_set[0]
    for i in range(1, len(ss_set)):
        print(f'Predicting {ss_set[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(ss_set[i]["graph"], start["graph"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()


# a FW1_2 dataset, with the observations stored in numpy arrays

# In[21]:


fwd = forward([1,2], obs_storage = 'numpy')

print('Data points contain the values: ')
for key, value in fwd[0][0].items():
    print(f'{key}: {type(value)}, ', end='')
print()
print()

for ss_set in fwd:
    print('Snapshots at: ', sep='', end='')
    for ss in ss_set:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = ss_set[0]
    for i in range(1, len(ss_set)):
        print(f'Predicting {ss_set[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(ss_set[i]["node_states"], start["node_states"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()


# a BW1_4 dataset, with the observations stored as pytorch geometric data objects

# In[22]:


bwd = backward([1,4], obs_storage = 'torch')

print('Data points contain the values: ')
for key, value in bwd[0][0].items():
    print(f'{key}: {type(value)}, ', end='')
print()
print()

for ss_set in bwd:
    print('Snapshots at: ', sep='', end='')
    for ss in ss_set:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = ss_set[0]
    for i in range(1, len(ss_set)):
        print(f'Predicting {ss_set[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(ss_set[i]["graph"], start["graph"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()
