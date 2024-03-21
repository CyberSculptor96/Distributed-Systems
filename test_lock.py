import threading
import unittest
from server import LockManager
import time

'''
    更为精细和自动化的测试模块，使用 unittest 测试框架
    主要测试点：文件锁机制，包括对文件的并发读和并发写
'''

class TestLockManager(unittest.TestCase):
    def setUp(self):
        self.lock_manager = LockManager()
        self.filename = "testfile.txt"
        self.read_locks_acquired = 0
        self.write_lock_acquired = False
        self.lock = threading.Lock()  # 用于保护对共享状态的访问

    def read_operation(self):
        self.lock_manager.acquire_read_lock(self.filename)
        with self.lock:
            self.read_locks_acquired += 1
        # 模拟读取操作的延迟
        time.sleep(0.1)
        self.lock_manager.release_lock(self.filename)
        with self.lock:
            self.read_locks_acquired -= 1

    def write_operation(self):
        self.lock_manager.acquire_write_lock(self.filename)
        with self.lock:
            self.write_lock_acquired = True
            # 验证在写操作开始前，没有读操作正在进行
            self.assertEqual(self.read_locks_acquired, 0)
        # 模拟写入操作的延迟
        time.sleep(0.1)
        self.lock_manager.release_lock(self.filename)
        with self.lock:
            self.write_lock_acquired = False

    def test_concurrent_readers(self):
        reader_threads = [threading.Thread(target=self.read_operation) for _ in range(5)]
        for thread in reader_threads:
            thread.start()
        for thread in reader_threads:
            thread.join()

    def test_write_requires_exclusivity(self):
        reader_threads = [threading.Thread(target=self.read_operation) for _ in range(5)]
        writer_thread = threading.Thread(target=self.write_operation)

        for thread in reader_threads:
            thread.start()
        # 稍微等待，让读者线程先启动

        time.sleep(0.1)
        writer_thread.start()

        for thread in reader_threads:
            thread.join()
        writer_thread.join()

        # 验证写操作是否已经完成
        self.assertFalse(self.write_lock_acquired)


if __name__ == "__main__":
    unittest.main()