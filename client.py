# client.py

import grpc
import file_system_pb2
import file_system_pb2_grpc
from collections import OrderedDict

class LruCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)  # mark as recently used
            return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # remove least recently used


class ClientCache:
    def __init__(self, size):
        self.cache = LruCache(size)

    def get_from_cache(self, filename):
        # Retrieve file data from cache if available
        return self.cache.get(filename)

    def update_cache(self, filename, data):
        # Update cache with new data
        self.cache.put(filename, data)


# 使用客户端缓存
cache = ClientCache(size=3)


# 创建文件
def create_file(stub, filename, user='hhj'):
    request = file_system_pb2.CreateFileRequest(filename=filename, user=user)
    response = stub.CreateFile(request)
    print(f"File {filename} created by user {user}:", response.success)


# 读取文件
def read_file(stub, filename, user='hhj'):
    file_data = cache.get_from_cache(filename)
    if file_data is None:
        # 如果文件不在缓存中，则从 server 中读取
        request = file_system_pb2.ReadFileRequest(filename=filename, user=user)
        response = stub.ReadFile(request)
        file_data = response.data
        # 将该文件更新到客户端缓存中
        cache.update_cache(filename, file_data)
    else:
        # 文件在客户端缓存中，直接读取即可
        print(f"Retrieved {filename} from cache.")
    print(f"File {filename} read by user {user}, content:", file_data)


# 写入文件
def write_file(stub, filename, data, user='hhj'):
    request = file_system_pb2.WriteFileRequest(filename=filename, data=data, user=user)
    response = stub.WriteFile(request)
    print(f"File {filename} written by user {user}:", response.success)


# 删除文件
def delete_file(stub, filename, user='hhj'):
    request = file_system_pb2.DeleteFileRequest(filename=filename, user=user)
    response = stub.DeleteFile(request)
    print(f"File {filename} deleted by user {user}:", response.success)


# 运行客户端，进行文件操作
def run():
    with grpc.insecure_channel('127.0.0.1:50053') as channel:
        # # 使用 gRPC 进行远程过程调用与 server 通信
        stub = file_system_pb2_grpc.FileSystemStub(channel)

        # 创建一个新的文件，并写入信息
        create_file(stub, "testfile.txt")
        write_file(stub, "testfile.txt", b"Hello SYSU")

        # 读取文件，可以选择不同的用户进行多次读取
        read_file(stub, "testfile.txt", "hhj")
        read_file(stub, "testfile.txt", "hhj")
        # 删除文件
        delete_file(stub, "testfile.txt")


if __name__ == '__main__':
    run()


'''
    多用户测试：使用 python 多线程模块模拟多用户的并发访问
'''

# import concurrent.futures
#
# # 单个用户的一个完整操作序列，可按需进行解耦
# def user_operations(stub, username):
#     user_mapping = {
#         "hhj": 1,
#         "Smith Huang": 2
#     }
#     default_mapping = 3
#     filename = f"testfile_{user_mapping.get(username, default_mapping)}.txt"
#     create_file(stub, filename, username)
#     content = f"Hello SYSU, {username}"
#     write_file(stub, filename, content.encode(), username)
#     read_file(stub, filename, username)
#     delete_file(stub, filename, username)
#
# def run_concurrently():
#     with grpc.insecure_channel('127.0.0.1:50053') as channel:
#         stub = file_system_pb2_grpc.FileSystemStub(channel)
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             executor.submit(user_operations, stub, "hhj")
#             executor.submit(user_operations, stub, "Smith Huang")
#             executor.submit(user_operations, stub, "Zhang San")
#
#
# if __name__ == '__main__':
#     run_concurrently()