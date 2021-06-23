from multiprocessing import Manager, Pool

input_list = ['A', 'B', 'C', 'D', 'E', 'F']

manager = Manager()
shared_list = manager.list()


def do_stuff(element):
    global shared_list
    element_dict = {}
    element_dict['name'] = element
    shared_list.append(element_dict)
    if len(shared_list) > 3:
        print('list > 3')
    print(shared_list)


pool = Pool(processes=8)
pool.map(do_stuff, input_list)
pool.close()
