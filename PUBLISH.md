# 如何将linkis-python-sdk发布到PyPI
# How to Publish linkis-python-sdk to PyPI

本文档描述了如何构建并将linkis-python-sdk包发布到PyPI，以便用户可以通过pip安装。
This document describes how to build and publish the linkis-python-sdk package to PyPI so that users can install it via pip.

## 准备工作
## Preparation

1. 确保你已经安装了必要的工具：
1. Make sure you have the necessary tools installed:

```bash
pip install build twine
```

2. 更新版本号：
2. Update the version number:
   - 在`linkis_python_sdk/__init__.py`中更新`__version__`变量
   - Update the `__version__` variable in `linkis_python_sdk/__init__.py`

3. 确认所有文件已添加到git：
3. Confirm all files have been added to git:
   - `setup.py`
   - `pyproject.toml`
   - `MANIFEST.in`
   - `README.md`
   - `LICENSE`
   - `.gitignore`
   - `setup.cfg`

## 构建包
## Build the Package

执行以下命令构建分发包：
Execute the following command to build distribution packages:

```bash
python -m build
```

这将在`dist/`目录下创建源码包(`.tar.gz`)和轮子包(`.whl`)。
This will create source packages (`.tar.gz`) and wheel packages (`.whl`) in the `dist/` directory.

## 测试包
## Test the Package

在发布到PyPI之前，建议先测试安装：
Before publishing to PyPI, it's recommended to test the installation:

```bash
pip install dist/linkis_python_sdk-x.y.z-py3-none-any.whl
```

## 上传到TestPyPI（可选）
## Upload to TestPyPI (Optional)

先上传到TestPyPI测试是一个好习惯：
It's good practice to first upload to TestPyPI for testing:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

然后测试从TestPyPI安装：
Then test installing from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ linkis-python-sdk
```

## 上传到PyPI
## Upload to PyPI

一切就绪后，上传到真正的PyPI：
When everything is ready, upload to the actual PyPI:

```bash
twine upload dist/*
```

## 验证安装
## Verify Installation

确认包已成功发布：
Confirm the package has been successfully published:

```bash
pip install linkis-python-sdk
```

## 相关链接
## Related Links

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Twine: https://twine.readthedocs.io/
- Python Packaging User Guide: https://packaging.python.org/ 