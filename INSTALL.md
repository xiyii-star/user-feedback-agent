# 安装说明

## 推荐环境

- **Python 版本**: 3.9 - 3.11（推荐 3.10 或 3.11）
- **操作系统**: Windows / macOS / Linux

## 安装步骤

### 方案1：使用 Conda（强烈推荐）

```bash
# 创建新环境
conda create -n feedback python=3.11
conda activate feedback

# 安装依赖
pip install -r requirements.txt
```

### 方案2：直接安装

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install langchain langchain-community langchain-openai openai python-dotenv faiss-cpu
```

## 验证安装

```bash
python -c "import langchain; import faiss; print('安装成功')"
```

## 常见问题

### Q: Python 3.13 安装失败？
A: Python 3.13 太新，很多包还不支持。请使用 Python 3.9-3.11。

### Q: numpy 编译失败？
A: Windows 需要 C++ 编译器。建议：
1. 使用 Conda 环境（推荐）
2. 使用 Python 3.9-3.11（有预编译包）
3. 安装 Visual Studio Build Tools

### Q: faiss-cpu 安装失败？
A: 确保使用 Python 3.9-3.11，并尝试：
```bash
conda install -c conda-forge faiss-cpu
```

### Q: 推荐的安装方式？
A: 使用 Conda 创建 Python 3.11 环境，最稳定可靠。
