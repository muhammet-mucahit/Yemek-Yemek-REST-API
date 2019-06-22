from apriori import Apriori

dataset = [
    ['Elma', 'Yag'],
    ['Elma', 'Yag', 'Cikolata', 'Ekmek'],
    ['Elma', 'Cikolata'],
    ['Elma', 'Cikolata'],
]

minsup = 0.3
minconf = 0.6

apriori = Apriori(dataset, minsup, minconf)
#apriori.set_selected_items(['1'])
apriori.run()
apriori.print_frequent_itemset()
result = apriori.print_rule()

print(result)

for res in result:
    x = res.split(' ==> ')
    print(x[0])
    print(x[1])
    # print(res[1])
