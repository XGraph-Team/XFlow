from FlowTasks import forward, backward, graph_eval



# ### Testing / Examples

# a FW1 dataset, with the observations stored as attributes to a networkx graph

# In[23]:


output = forward(1, obs_type = 'networkx', num_results=5)

#print observation type
print('Observations are of type:', type(output[0]['observations'][0]['observation']), end='\n\n')

for result in output:
    observations = result['observations']
    graph = result['base_graph']
    sir = result['SIR_model']
    
    #print sir values for this result
    print('SIR model has values: ', sep='', end='')
    print(f'beta = {round(sir["beta"],3)}, gamma = {round(sir["gamma"],3)}')
    
    #print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = observations[0]
    for i in range(1, len(observations)):
        print(f'Predicting {observations[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(observations[i]["observation"], start["observation"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()


# a FW1_2 dataset, with the observations stored in numpy arrays

# In[24]:


output = forward([1,2], obs_type = 'numpy', num_results=5)

#print observation type
print('Observations are of type:', type(output[0]['observations'][0]['observation']), end='\n\n')

for result in output:
    observations = result['observations']
    graph = result['base_graph']
    sir = result['SIR_model']
    
    #print sir values for this result
    print('SIR model has values: ', sep='', end='')
    print(f'beta = {round(sir["beta"],3)}, gamma = {round(sir["gamma"],3)}')
    
    #print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = observations[0]
    for i in range(1, len(observations)):
        print(f'Predicting {observations[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(observations[i]["observation"], start["observation"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()


# a BW1_4 dataset, with the observations stored as pytorch geometric data objects

# In[25]:


output = backward([1,4], obs_type = 'torch', num_results=5)

#print observation type
print('Observations are of type:', type(output[0]['observations'][0]['observation']), end='\n\n')

for result in output:
    observations = result['observations']
    graph = result['base_graph']
    sir = result['SIR_model']
    
    #print sir values for this result
    print('SIR model has values: ', sep='', end='')
    print(f'beta = {round(sir["beta"],3)}, gamma = {round(sir["gamma"],3)}')
    
    #print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss["time"]}, ', end='')
    print()
    
    start = observations[0]
    for i in range(1, len(observations)):
        print(f'Predicting {observations[i]["time"]} is the same as {start["time"]} - ', end='')
        eval_dict = graph_eval(observations[i]["observation"], start["observation"])
        for key, value in eval_dict.items():
            print(f'{key}: {round(value,3)}, ', end='')
        print()
    print()
