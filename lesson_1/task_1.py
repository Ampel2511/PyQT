from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate


def host_ping(addresses):
    result_list = {'Узел доступен': [],
                   'Узел недоступен': []}
    for address in addresses:
        try:
            address = ip_address(address)
        except:
            pass
        p = Popen(f'ping {address}', shell=False, stdout=PIPE)
        result = p.wait()
        if result == 0:
            print(f'Узел доступен - {address}')
            result_list['Узел доступен'].append(f'{address}\n')
        else:
            print(f'Узел недоступен - {address}')
            result_list['Узел недоступен'].append(f'{address}\n')
    return print(tabulate(result_list, headers='keys', stralign='center'))


addresses = ["234.35.43.1", "8.8.8.8", "google.com", "yandex.ru", "324.345.23.65"]

if __name__ == '__main__':
    host_ping(addresses)
