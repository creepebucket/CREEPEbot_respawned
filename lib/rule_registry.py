import importlib.util
import sys
from pathlib import Path

from lib import logger

# ---------- 注册表 ----------
_registry = []  # 存放所有自动实例化的对象

def get_registry():
    """返回注册表（只读副本或直接引用）"""
    return _registry

# ---------- 装饰器 ----------
def register(cls):
    """
    类装饰器：自动实例化被装饰的类，并将实例添加到注册表。
    注意：这里要求被装饰的类可以用无参构造器实例化。
    如需传参，可在此处修改逻辑（例如从配置文件读取）。
    """
    instance = cls()
    _registry.append(instance)
    # 可选：在实例上保存一些元信息
    instance._registered_class = cls.__name__
    logger.debug(f'已注册事件处理规则 `{cls}`')
    return cls  # 返回原类，不改变类定义

# ---------- 动态加载模块 ----------
def _load_module_from_path(file_path: Path):
    """
    从给定 .py 文件动态加载模块，执行其中代码。
    使用文件路径作为模块名以避免冲突（简单把路径中的特殊字符替换掉）。
    """
    module_name = None
    parts = file_path.resolve().parts
    if 'nb_plugins' in parts:
        i = parts.index('nb_plugins')
        module_name = '.'.join(parts[i:]).replace('.py', '')
    else:
        relative = file_path.relative_to(file_path.anchor)
        module_name = str(relative).replace('/', '_').replace('\\', '_').replace('.py', '')

    # 如果已经加载过同名模块，先移除（避免重复加载时旧代码残留）
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# ---------- 扫描入口 ----------
def scan_and_register(root_dir: str, pattern: str = "*.py"):
    """
    递归扫描 root_dir 下所有匹配 pattern 的文件，动态加载并自动注册。
    默认扫描所有 .py 文件，可通过 pattern 过滤（如 "plugin_*.py"）。
    """
    global _registry
    _registry.clear()
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"{root_dir} 不是一个有效目录")

    for py_file in root.rglob(pattern):
        # 避免加载包入口导致副作用（例如 nonebot 的 on_message 注册两遍）
        if py_file.name == "__init__.py":
            continue
        try:
            _load_module_from_path(py_file)
        except Exception as e:
            # 记录加载失败的文件，但不中断整个扫描
            logger.error(f"警告: 无法加载 {py_file} -> `{e}`")

    _registry = sorted(_registry, key=lambda t: t.priority, reverse=True)
