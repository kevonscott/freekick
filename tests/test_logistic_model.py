# X = [] # home
# X1 = [] # away
# In [86]: for x in list(permutations(['A','B','C','D','E','F'],2)):
#     ...:     X.append(x[0])
#     ...:     X1.append(x[1])
#     ...:

# In [89]: choice = []

# In [90]: for i in X:
#     ...:     choice.append(random.choice([-1,0,1]))
#     ...:

# In [91]: print(choice)
# [0, 0, 0, -1, 1, -1, 0, -1, -1, -1, 1, 0, -1, 0, -1, 1, 0, 1, -1, 0, -1, 0, 0, 0, 1, 1, -1, -1, -1, 1]

# In [92]:

# rand_dates = []
# In [102]: for h in X:
#      ...:     val = str(random.choice(range(1700,2021))) + '-' + str(random.choice(range(1,13))) + '-' + str(random.choice(range(1,32)))
#      ...:     rand_dates.append(val)
#      ...:

# In [103]: print(rand_dates)
# ['1761-10-18', '1946-7-13', '1991-10-7', '1709-11-30', '1799-2-25', '1822-6-6', '1799-10-26', '2020-6-15', '1926-9-10', '1966-6-23', '1902-1-5', '1836-7-12', '1910-6-12', '1992-2-11', '1898-1-13', '1841-8-1', '1801-9-7', '1817-2-8', '1994-3-11', '1989-10-22', '1917-11-5', '1784-9-31', '1987-1-7', '1804-6-28', '1920-8-13', '1731-4-29', '1805-11-13', '1789-11-7', '1714-4-10', '1878-8-12']

# In [104]:


# if __name__=='__main__':
#     home_teams = ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'D', 'D', 'D', 'D', 'D', 'E', 'E', 'E', 'E', 'E', 'F', 'F', 'F', 'F', 'F']
#     away_teams = ['B', 'C', 'D', 'E', 'F', 'A', 'C', 'D', 'E', 'F', 'A', 'B', 'D', 'E', 'F', 'A', 'B', 'C', 'E', 'F', 'A', 'B', 'C', 'D', 'F', 'A', 'B', 'C', 'D', 'E']
#     rand_dates = ['1761-10-18', '1946-7-13', '1991-10-7', '1709-11-30', '1799-2-25', '1822-6-6', '1799-10-26', '2020-6-15', '1926-9-10', '1966-6-23', '1902-1-5', '1836-7-12', '1910-6-12', '1992-2-11', '1898-1-13', '1841-8-1', '1801-9-7', '1817-2-8', '1994-3-11', '1989-10-22', '1917-11-5', '1784-9-31', '1987-1-7', '1804-6-28', '1920-8-13', '1731-4-29', '1805-11-13', '1789-11-7', '1714-4-10', '1878-8-12']
#     data = pd.DataFrame({'date': rand_dates, 'home': home_teams,'away': away_teams })
#     data.index = data['date'] + '_' + data['home'] + '_' + data['away']
#     data = data.drop(columns=['date'])

#     y = [0, 0, 0, -1, 1, -1, 0, -1, -1, -1, 1, 0, -1, 0, -1, 1, 0, 1, -1, 0, -1, 0, 0, 0, 1, 1, -1, -1, -1, 1]
#     data = pd.get_dummies(data, columns=['home','away'], prefix=['home', 'away'])

#     mod = SoccerLogisticModel(data, y)
#     mod.fit()

#     coeff = mod.get_coeff()
#     win_probability = mod.predict_probability(data)
#     winners = mod.predict_winner(data)
