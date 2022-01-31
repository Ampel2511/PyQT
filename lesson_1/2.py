from ipaddress import ip_address
from task_1 import host_ping


def host_range_ping(start_ip, count):
    ip_list = [start_ip]
    start_ip = ip_address(start_ip)
    while count > 0:
        start_ip += 1
        ip_list.append(str(start_ip))
        count -= 1
    print(ip_list)
    return host_ping(ip_list)


start_ip = '8.8.8.8'
count = 5

if __name__ == '__main__':
    host_range_ping(start_ip, count)
