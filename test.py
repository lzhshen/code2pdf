import os
import unittest
from code2pdf import filter_directories

class TestFilterDirectories(unittest.TestCase):
    def setUp(self):
        # 设置测试环境和数据
        self.dirs = ['dir1', 'dir2', 'dir3']
        self.current_path = '/home/user/project'
        self.root_dir = '/home/user'
        self.spec = pathspec.PathSpec.from_lines('gitignore', ['*.ignore', 'dir2/'])

    def test_filter_directories(self):
        # 调用待测函数
        filter_directories(self.dirs, self.current_path, self.spec, self.root_dir)
        # 断言函数结果是否符合预期
        self.assertEqual(self.dirs, ['dir1', 'dir3'])

    def test_filter_directories_no_match(self):
        # 测试不忽略任何目录的情况
        spec_no_match = pathspec.PathSpec.from_lines('gitignore', ['*.pdf', '*.docx'])
        filter_directories(self.dirs, self.current_path, spec_no_match, self.root_dir)
        # 断言所有目录都未被忽略
        self.assertEqual(self.dirs, ['dir1', 'dir2', 'dir3'])

    def test_filter_directories_all_match(self):
        # 测试所有目录都被忽略的情况
        spec_all_match = pathspec.PathSpec.from_lines('gitignore', ['*', 'dir1/', 'dir3/'])
        filter_directories(self.dirs, self.current_path, spec_all_match, self.root_dir)
        # 断言没有目录被保留
        self.assertEqual(self.dirs, [])

if __name__ == '__main__':
    unittest.main()