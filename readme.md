# 基于gRPC的分布式文件系统（2023年秋季学期）



| 班级                           | 学号     | 姓名   |
| ------------------------------ | :------- | ------ |
| 计科（人工智能与大数据实验班） | 21307404 | 黄河锦 |


## 一、项目介绍

　　本课程项目旨在设计一个简单的分布式文件系统。该文件系统采用 client-server 架构，具有基本的访问、打开、删除、缓存等功能，同时具有一致性、支持多用户特点。

### 1.1 文件操作和通信协议

- 使用Python实现所有功能，利用Python的多进程和网络库（如`socket`或`http`）。
- 文件系统节点之间的通信采用RPC模式，可以选择`XML-RPC`或`gRPC`。`gRPC`基于HTTP/2，性能更优，且支持多语言，因此我们选择`gRPC`。

### 1.2 文件操作类型

　　实现以下基本文件操作：

- 创建（Create）
- 删除（Delete）
- 访问（Read/Write）

### 1.3 关键技术

#### 1.3.1 客户端缓存

- 客户端缓存可以使用内存（如Python的字典）或磁盘文件（如SQLite数据库）。
- 缓存策略可采用LRU（Least Recently Used）算法，优化性能。

#### 1.3.2 数据副本和一致性

- 数据副本：创建文件时在不同的物理机器上创建多个副本。
- 一致性：可以选择CAP定理中的一致性和可用性。考虑到可操作性，我们可以选择最终一致性模型来平衡。

#### 1.3.3 多用户支持和文件锁

- 使用文件锁机制来支持并行读写，确保同一时间只有一个用户可以写入特定文件。
- 读写锁（共享锁和排他锁）可以保证读者不会阻塞读者，但写者会阻塞所有其他操作。

#### 1.3.4 访问权限控制

​		实现基本的访问控制列表（ACL），根据用户身份控制文件访问权限。

### 1.3.5 本地测试和验证

​		使用 python  的 `concurrent.futures` 开发多线程以模拟多用户对分布式文件系统的并发访问。进行相关测试。

​		在 python  提供的 `unittest` 测试框架中对文件锁的功能进行了测试。



## 二、实现细节

  在这个项目中，服务器端负责文件的存储、元数据管理、副本控制、锁定机制和访问控制，而客户端则负责维护本地缓存。对应的 Top-Down 设计的类如下： 

- **服务器端 (`server.py`):**  

	- MetadataManager
	- **FileSystemServer** 
	- ReplicationManager 
	- LockManager
	- AccessControl 

- **客户端 (`client.py`):**  
- ClientCache 


## 三、环境配置

### 3.1 技术选型和安装

首先，需要安装必要的Python库，比如 `grpcio` 和 `grpcio-tools`。可以使用pip进行安装： 

 ```
 python pip install grpcio grpcio-tools
 ```



### 3.2 定义gRPC服务

#### 定义 Proto 文件 file_system.proto

定义文件系统的操作，例如创建、读取、写入和删除文件。

```protobuf
// file_system.proto

syntax = "proto3";

service FileSystem {
  rpc CreateFile(CreateFileRequest) returns (CreateFileResponse);
  rpc ReadFile(ReadFileRequest) returns (ReadFileResponse);
  rpc WriteFile(WriteFileRequest) returns (WriteFileResponse);
  rpc DeleteFile(DeleteFileRequest) returns (DeleteFileResponse);
}

message CreateFileRequest {
  string filename = 1;
  string user = 2;
}

message CreateFileResponse {
  bool success = 1;
}

message ReadFileRequest {
  string filename = 1;
  string user = 2;
}

message ReadFileResponse {
  bytes data = 1;
}

message WriteFileRequest {
  string filename = 1;
  bytes data = 2;
  string user = 3;
}

message WriteFileResponse {
  bool success = 1;
}

message DeleteFileRequest {
  string filename = 1;
  string user = 2;
}

message DeleteFileResponse {
  bool success = 1;
}
```

#### 3.3 生成gRPC代码

使用 `grpcio-tools` 从proto文件生成Python代码:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_system.proto 
```



## 四、运行服务器和客户端

### 4.1 运行服务器:

```sh
python .\server.py
```

### 4.2 在另一个终端运行客户端:

```sh 
python .\client.py 
```



## 五、运行代码

`server.py`：

```python
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_system_pb2_grpc.add_FileSystemServicer_to_server(FileSystemServicer(), server)
    server.add_insecure_port('127.0.0.1:50053')
    server.start()
    print('Server running on port 50053...')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

`client.py`:

```python
def run():
    # with grpc.insecure_channel('localhost:50051') as channel:
    with grpc.insecure_channel('127.0.0.1:50053') as channel:
        stub = file_system_pb2_grpc.FileSystemStub(channel)
        create_file(stub, "testfile.txt")
        write_file(stub, "testfile.txt", b"Hello World")
        read_file(stub, "testfile.txt", "xyz")
        read_file(stub, "testfile.txt", "xyz")
        delete_file(stub, "testfile.txt")

if __name__ == '__main__':
    run()
```



