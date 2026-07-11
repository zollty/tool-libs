# 文件工具箱

核心工具见下文：
```python
def delete_dir(folder_path, with_confirm=False):
    """快速删除文件夹及其所有内容，优先调用 fast_delete_win32，如不支持再调用fast_delete """
    
def fast_delete(folder_path):
    """底层方法，快速删除文件夹及其所有内容"""
    
def fast_delete_win32(folder_path):
    """底层方法，Windows系统下的极速删除方案"""
```

### 查找目录A下面的每一个文件在目录B中是否存在，分别列出存在的文件在A及B目录的路径，以及不存在的文件的路径
```bash
python compare_directories_files.py 
# 然后根据提示输入两个目录的路径

   # 直接调用函数：比较两个目录
   compare_directories_by_name_and_time("/path/to/dir_a", "/path/to/dir_b")
   
```

### 查找目录A下面的所有子文件夹在目录B中是否存在，列出不存在的文件夹的路径
如果父目录不存在，就不要列出子目录  
`compare_directories.py`


### 在某几个目录下面，查找定制的某几个文件夹名称是否存在
递归查找，可以设置查找深度。找到一个后不会停止搜索，但是会停止对找到目录的子目录进行搜索。  
`find_folder_in_dirs.py`

### 对比两个目录及文件的差异，递归对比子目录
只对比文件名称，不对比内容。以左边目录为标准，以目录树的形式打印出增加和减少的文件及文件夹（对于新增或减少的文件夹，只需要打印文件夹名称，不需要打印文件夹里面的内容）  
`compare_dirs_with_only_name.py`


