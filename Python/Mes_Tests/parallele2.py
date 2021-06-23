from multiprocessing import Manager, Pool

manager = Manager()
shared_list = manager.list()


def process(i):
    global shared_list
    shared_list.append(i * i)


pool = Pool(processes=8)
pool.map(process, [i for i in range(10)])
pool.close()
print(shared_list)
