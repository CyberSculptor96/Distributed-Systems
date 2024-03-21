# 基于gRPC的分布式文件系统（2023年秋季学期）



| 班级                           | 学号     | 姓名   |
| ------------------------------ | :------- | ------ |
| 计科（人工智能与大数据实验班） | 21307404 | 黄河锦 |



## 环境配置

### 技术选型和安装

首先，需要安装必要的Python库，比如 `grpcio` 和 `grpcio-tools`。可以使用pip进行安装： 

 ```
 python pip install grpcio grpcio-tools
 ```



### 定义gRPC服务

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

#### 生成gRPC代码

使用 `grpcio-tools` 从proto文件生成Python代码:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_system.proto 
```



## 运行服务器和客户端

### 运行服务器:

```sh
python .\server.py
```

### 在另一个终端运行客户端:

```sh 
python .\client.py 
```



## 运行代码

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



