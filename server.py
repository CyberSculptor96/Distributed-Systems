# server.py

import os
import grpc
from concurrent import futures
import file_system_pb2
import file_system_pb2_grpc
import json
import threading
import datetime


# 1. 管理文件的元数据
class MetadataManager:
    def __init__(self):
        self.files_metadata = {}
        self.metadata_lock = threading.Lock()
        self.metadata_file = "metadata.json"
        self.load_metadata()

    def load_metadata(self):
        # 从 json 文件中以字典形式加载元数据
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.files_metadata = json.load(f)

    def save_metadata(self):
        # 以字典形式将元数据保存为 json 文件
        with open(self.metadata_file, 'w') as f:
            json.dump(self.files_metadata, f, indent=4)

    def create_file_metadata(self, filename, replica_info):
        # 为新文件创建并保存一个元数据
        with self.metadata_lock:
            if filename not in self.files_metadata:
                self.files_metadata[filename] = {
                    'size': 0,
                    'created_at': str(datetime.datetime.now()),
                    'modified_at': str(datetime.datetime.now()),
                    # 记录文件存储的副本信息
                    'replicas': replica_info
                }
                self.save_metadata()
                return True
            else:
                return False

    def get_file_metadata(self, filename):
        # 获取已创建文件的元数据
        with self.metadata_lock:
            return self.files_metadata.get(filename, None)

    def update_file_metadata(self, filename, metadata):
        # 更新已创建文件的元数据
        with self.metadata_lock:
            if filename in self.files_metadata:
                self.files_metadata[filename].update(metadata)
                self.files_metadata[filename]['modified_at'] = str(datetime.datetime.now())
                self.save_metadata()
                return True
            else:
                return False

    def delete_file_metadata(self, filename):
        # 删除已创建文件的元数据
        with self.metadata_lock:
            if filename in self.files_metadata:
                del self.files_metadata[filename]
                self.save_metadata()
                return True
            else:
                return False


# 2. 对文件的副本进行管理
class ReplicationManager:
    def __init__(self, replica_dirs):
        # 副本所在的目录
        self.replica_dirs = replica_dirs
        for dir in self.replica_dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def get_replica_info(self, filename):
        # 获取副本信息，例如存储副本的路径列表
        replica_paths = [os.path.join(replica_dir, filename) for replica_dir in self.replica_dirs]
        return replica_paths

    def replicate_data(self, filename, data):
        # 将副本复制到所有节点上，实现一致性
        for replica_dir in self.replica_dirs:
            replica_path = os.path.join(replica_dir, filename)
            with open(replica_path, 'wb') as replica_file:
                replica_file.write(data)
        return True

    def delete_replica(self, filename):
        # 从所有副本节点中删除一个文件
        for replica_dir in self.replica_dirs:
            replica_path = os.path.join(replica_dir, filename)
            if os.path.exists(replica_path):
                os.remove(replica_path)
        return True

    def synchronize_replicas(self, filename):
        # 将文件同步到所有的副本节点中
        # 构建主副本路径
        primary_path = os.path.join(self.replica_dirs[0], filename)
        if os.path.exists(primary_path):
            with open(primary_path, 'rb') as primary_file:
                # 读取主副本文件的数据，并将其复制到所有副本目录中
                data = primary_file.read()
                for replica_dir in self.replica_dirs[1:]:
                    # 构建副本路径，打开副本文件并写入数据
                    replica_path = os.path.join(replica_dir, filename)
                    with open(replica_path, 'wb') as replica_file:
                        replica_file.write(data)
        return True


# 3. 文件锁定机制
class LockManager:
    def __init__(self):
        # 初始化一个字典来保存文件锁的状态
        self.locks = {}
        self.locks_lock = threading.Lock()  # 保护对locks字典的访问

    def _get_lock(self, filename):
        with self.locks_lock:
            if filename not in self.locks:
                # 对于每个文件，我们使用一个读写锁，允许多个线程同时读取
                self.locks[filename] = threading.RLock()
            return self.locks[filename]

    def acquire_read_lock(self, filename):
        # 获取读锁，如果已经有读锁，则增加计数
        file_lock = self._get_lock(filename)
        file_lock.acquire()

    def acquire_write_lock(self, filename):
        # 获取写锁，如果已经有读锁或写锁，则阻塞直到锁释放
        file_lock = self._get_lock(filename)
        file_lock.acquire()

    def release_lock(self, filename):
        # 释放读或写锁，减少计数
        file_lock = self._get_lock(filename)
        if file_lock._is_owned():  # 检查当前线程是否拥有锁
            file_lock.release()


# 4. 访问控制列表
class AccessControl:
    def __init__(self):
        # 初始化一个字典来保存用户对文件的权限
        self.permissions = {'testfile.txt': {'hhj': ['read']},
                            'testfile_1.txt': {'hhj': ['read']},
                            'testfile_2.txt': {'hhj': ['read']}
                            }

    def set_permission(self, user, filename, operation):
        # 设置用户对文件的操作权限
        if filename not in self.permissions:
            self.permissions[filename] = {}
        self.permissions[filename][user] = operation

    def check_permission(self, user, filename, operation):
        # 检查用户是否对文件具有操作权限
        print(self.permissions)
        file_permissions = self.permissions.get(filename, {})
        user_permissions = file_permissions.get(user, [])
        return operation in user_permissions


# 5. 集成上述功能的分布式文件系统
class FileSystemServicer(file_system_pb2_grpc.FileSystemServicer):
    def __init__(self, storage_path="storage"):
        # 定义文件存储的目录
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        # 1. 文件元数据管理器
        self.metadata_manager = MetadataManager()

        # 2. 文件副本管理器
        self.replication_manager = ReplicationManager(
            ['replica1', 'replica2', 'replica3'])

        # 3. 文件锁定机制
        self.lock_manager = LockManager()

        # 4. 访问控制列表
        self.access_control = AccessControl()
        self.access_control.set_permission('Smith Huang', 'testfile.txt', ['read'])
        self.access_control.set_permission('Smith Huang', 'testfile_1.txt', ['read'])
        self.access_control.set_permission('Smith Huang', 'testfile_2.txt', ['read'])

    def CreateFile(self, request, context):
        file_path = os.path.join(self.storage_path, request.filename)
        # 获取一个写锁
        self.lock_manager.acquire_write_lock(request.filename)
        try:
            if not os.path.exists(file_path):
                try:
                    # 创建一个空文件
                    open(file_path, 'w').close()
                    # 将数据扩散到各副本节点
                    if self.replication_manager.replicate_data(request.filename, b''):
                        # 获取副本信息
                        replica_info = self.replication_manager.get_replica_info(request.filename)
                        # 创建文件的元数据，并包括副本信息
                        self.metadata_manager.create_file_metadata(request.filename, replica_info)
                        # 此处给所有创建文件的用户都添加了读取文件的权限
                        self.access_control.set_permission(request.user, request.filename, ['read'])
                        return file_system_pb2.CreateFileResponse(success=True)
                    else:
                        context.set_details('Metadata creation failed.')
                        context.set_code(grpc.StatusCode.INTERNAL)
                        return file_system_pb2.CreateFileResponse(success=False)
                # 若文件无法正常创建，则抛出I/O异常
                except IOError as e:
                    context.set_details(str(e))
                    context.set_code(grpc.StatusCode.INTERNAL)
                    return file_system_pb2.CreateFileResponse(success=False)
            # 若文件已创建，则不能重复创建，返回false
            else:
                context.set_details('File already exists.')
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                return file_system_pb2.CreateFileResponse(success=False)
        finally:
            # 确保写锁的释放
            self.lock_manager.release_lock(request.filename)

    def ReadFile(self, request, context):
        user = request.user  # 假设请求中包含了用户信息
        file_path = os.path.join(self.storage_path, request.filename)
        if os.path.exists(file_path):
            # 首先通过ACL检查用户是否有读取文件的权限
            if self.access_control.check_permission(user, request.filename, 'read'):
                # 若有权限，在读取文件之前需要先获取读锁
                self.lock_manager.acquire_read_lock(request.filename)
                try:
                    with open(file_path, 'rb') as file:
                        data = file.read()
                    return file_system_pb2.ReadFileResponse(data=data)
                except IOError as e:
                    context.set_details(str(e))
                    context.set_code(grpc.StatusCode.INTERNAL)
                    return file_system_pb2.ReadFileResponse(data=b"")
                finally:
                    # 确保最终释放读锁
                    self.lock_manager.release_lock(request.filename)
            else:
                # 用户无读取文件权限
                context.set_details('Permission denied.')
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                return file_system_pb2.ReadFileResponse(data=b"")
        else:
            context.set_details('File not found.')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return file_system_pb2.ReadFileResponse(data=b"")

    def WriteFile(self, request, context):
        file_path = os.path.join(self.storage_path, request.filename)
        # 首先获取一个写锁
        self.lock_manager.acquire_write_lock(request.filename)
        try:
            if os.path.exists(file_path):
                # 写入数据到主文件
                with open(file_path, 'wb') as file:
                    file.write(request.data)
                # 同步数据到各副本节点
                if self.replication_manager.replicate_data(request.filename, request.data):
                    # 获取副本信息
                    replica_info = self.replication_manager.get_replica_info(request.filename)
                    # 更新文件元数据，包括副本信息
                    self.metadata_manager.update_file_metadata(request.filename, {'replicas': replica_info})
                    return file_system_pb2.WriteFileResponse(success=True)
            else:
                context.set_details('File not found.')
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return file_system_pb2.ReadFileResponse(data=b"")
        except IOError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return file_system_pb2.WriteFileResponse(success=False)
        finally:
            # 确保写锁的释放
            self.lock_manager.release_lock(request.filename)

    def DeleteFile(self, request, context):
        file_path = os.path.join(self.storage_path, request.filename)
        if os.path.exists(file_path):
            try:
                # 删除主文件
                os.remove(file_path)
                # 删除副本文件
                if self.replication_manager.delete_replica(request.filename):
                    # 更新文件元数据，移除副本信息
                    self.metadata_manager.update_file_metadata(request.filename, {'replicas': []})
                    return file_system_pb2.DeleteFileResponse(success=True)
            except IOError as e:
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return file_system_pb2.DeleteFileResponse(success=False)
        else:
            context.set_details('File not found.')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return file_system_pb2.DeleteFileResponse(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_system_pb2_grpc.add_FileSystemServicer_to_server(FileSystemServicer(), server)
    server.add_insecure_port('127.0.0.1:50053')
    server.start()
    print('Server running on port 50053...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()