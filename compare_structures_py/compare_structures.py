import sys
import json

from typing import Union, Dict, List, Any, Set, Tuple
from copy import deepcopy
import re
from logzero import logger


def compare_structures(
    origin_data: Union[Dict, List],
    current_data: Union[Dict, List],
    path: str = "",
    check_value: bool = True,
    check_missing: bool = True,
    check_redundant: bool = False,
    check_type: bool = True,
    exclude_fields: Set[str] = None,
    deep_diff_contrast_config: Dict = None,
    open_log: bool = False,
) -> List[str]:
    """
    增强版结构对比函数（Python原生实现）
    :param origin_data: Origin数据
    :param current_data: Current数据
    :param path: 当前路径（递归用）
    :param check_value: 是否检查值差异
    :param check_missing: 是否检查缺失字段
    :param check_redundant: 是否检查冗余字段
    :param check_type: 是否检查类型差异
    :param exclude_fields: 排除字段白名单
    :param deep_diff_contrast_config: 对比配置参数
    :param open_log: 开启日志，默认关闭
    :return: 差异列表
    作者:崔浩浩
    功能
    识别以下差异：
    1. dict2相比dict1缺失的字段（包括嵌套结构）
    2. 相同字段的类型不一致
    3. 列表结构差异（长度、元素类型）
    4. 字段返回内容一致
    5. 剔除白名单字段检查
        示例：{"go_article_service", "user.medal"}
        功能：
        1. 支持嵌套路径 (如 "user.medal" 会跳过该字段及其子字段)
        2. 支持列表元素路径 (如 "tags")
        3. 完全匹配路径时跳过所有检查
    新增功能：
    1. 对列表使用Python原生代码进行深度对比
    2. 支持忽略列表顺序（ignore_order）
    3. 支持配置类型组参数（如数值精度、类型检查等）
    """

    # 内置函数定义开始
    def _compare_dicts(
        origin_dict: Dict,
        current_dict: Dict,
        path: str,
        check_value: bool,
        check_missing: bool,
        check_redundant: bool,
        check_type: bool,
        exclude_fields: Set[str],
        deep_diff_contrast_config: Dict,
        differences: List[str],
        open_log: bool,
    ) -> List[str]:
        """处理字典类型对比"""
        # 检查Origin字段
        for key in origin_dict:
            current_path = _format_path(f"{path}.{key}" if path else key)
            # 使用统一的排除检查函数
            if _should_exclude(current_path, exclude_fields):
                continue

            origin_val = origin_dict[key]

            # 字段存在性检查
            if key not in current_dict:
                if check_missing:
                    differences.append(
                        f"[字段缺失] {current_path} (Origin类型: {_type_detail(origin_val)})"
                    )
                continue

            current_val = current_dict[key]

            # 递归处理嵌套结构
            if isinstance(origin_val, (dict, list)):
                differences += compare_structures(
                    origin_val,
                    current_val,
                    current_path,
                    check_value,
                    check_missing,
                    check_redundant,
                    check_type,
                    exclude_fields,
                    deep_diff_contrast_config,
                    open_log,
                )
            else:
                # 值对开启
                if check_value:
                    # 第一步：快速等价判断（优先于类型检查，需要配置 ignore_type_in_groups）
                    if _is_equivalent_value(origin_val, current_val, deep_diff_contrast_config):
                        continue  # 跳过差异记录

                    # 第二步：类型冲突检查（考虑嵌套结构）
                    if check_type and not _is_same_type(
                        origin_val, current_val, deep_diff_contrast_config
                    ):
                        differences.append(
                            f"[类型冲突] {current_path} "
                            f"Origin类型: {_type_detail(origin_val)} → "
                            f"Current类型: {_type_detail(current_val)}"
                        )
                        continue

                    # 第三步：值对比
                    if origin_val != current_val:
                        differences.append(
                            f"[值变化] {current_path} "
                            f"Origin值: {_format_value(origin_val)} → "
                            f"Current值: {_format_value(current_val)}"
                        )
                # 值对比关闭
                else:
                    # 当关闭值对比时检查逻辑
                    differences = _special_value_check(
                        origin_val, current_val, current_path, differences
                    )
        # 冗余字段检查
        if check_redundant:
            for key in current_dict:
                if key not in origin_dict:
                    current_path = _format_path(f"{path}.{key}" if path else key)
                    # 使用统一的排除检查函数
                    if not _should_exclude(current_path, exclude_fields):
                        differences.append(
                            f"[冗余字段] {current_path} (Current类型: {_type_detail(current_dict[key])})"
                        )

        return differences

    def _compare_lists(
        origin_list: List,
        current_list: List,
        path: str,
        check_value: bool,
        check_missing: bool,
        check_redundant: bool,
        check_type: bool,
        exclude_fields: Set[str],
        deep_diff_contrast_config: Dict,
        differences: List[str],
        open_log: bool,
    ) -> List[str]:
        """列表对比逻辑"""
        # 值对比开启
        if check_value:
            differences = _compare_lists_native(
                origin_list,
                current_list,
                path,
                check_type,
                exclude_fields,
                deep_diff_contrast_config,
                differences,
                open_log,
            )
        # 值对比关闭
        else:
            # 不检查值时需要校验字段是否非空
            for i in range(min(len(origin_list), len(current_list))):
                elem_path = f"{path}[{i}]"
                if isinstance(origin_list[i], (dict, list)):
                    differences += compare_structures(
                        origin_list[i],
                        current_list[i],
                        elem_path,
                        check_value,
                        check_missing,
                        check_redundant,
                        check_type,
                        exclude_fields,
                        deep_diff_contrast_config,
                        open_log,
                    )
                else:
                    # 当关闭值对比时检查逻辑
                    differences = _special_value_check(
                        origin_list[i], current_list[i], elem_path, differences
                    )

                    # 基础类型对比
                    if check_type and not _is_same_type(
                        origin_list[i], current_list[i], deep_diff_contrast_config
                    ):
                        differences.append(
                            f"[类型冲突] {elem_path} "
                            f"Origin类型: {_type_detail(origin_list[i])} → "
                            f"Current类型: {_type_detail(current_list[i])}"
                        )
        return differences

    def _compare_lists_native(
        origin_list: List,
        current_list: List,
        path: str,
        check_type: bool,
        exclude_fields: Set[str],
        deep_diff_contrast_config: Dict,
        differences: List[str],
        open_log: bool,
    ) -> List[str]:
        """
        使用Python原生代码实现列表对比
        """
        if open_log:
            logger.info(
                f"_compare_lists_native: path={path}, "
                f"origin_len={len(origin_list)}, current_len={len(current_list)}"
            )

        ignore_order = deep_diff_contrast_config.get("ignore_order", True)

        # 如果忽略顺序，需要特殊处理
        if ignore_order:
            # 创建副本以避免修改原始数据
            origin_list_copy = deepcopy(origin_list)
            current_list_copy = deepcopy(current_list)

            # 记录匹配关系：origin_index -> current_index
            origin_matched = {}  # {origin_index: current_index}
            current_matched = set()  # 已匹配的current索引

            # 第一遍：精确匹配并记录匹配关系
            for i, origin_item in enumerate(origin_list_copy):
                for j, current_item in enumerate(current_list_copy):
                    if j in current_matched:
                        continue
                    # 检查是否匹配
                    if _items_match(origin_item, current_item, check_type, deep_diff_contrast_config):
                        origin_matched[i] = j
                        current_matched.add(j)
                        break

            # 记录未匹配的元素
            for i in range(len(origin_list_copy)):
                if i not in origin_matched:
                    elem_path = f"{path}[{i}]"
                    # 检查是否在排除字段中
                    if _should_exclude(elem_path, exclude_fields):
                        continue
                    differences.append(
                        f"[列表差异] {elem_path} (iterable_item_removed)"
                    )

            for j in range(len(current_list_copy)):
                if j not in current_matched:
                    elem_path = f"{path}[{j}]"
                    # 检查是否在排除字段中
                    if _should_exclude(elem_path, exclude_fields):
                        continue
                    differences.append(
                        f"[列表差异] {elem_path} (iterable_item_added)"
                    )

            # 对于已匹配的元素，递归对比（使用原始索引路径）
            # 优化：即使元素在_items_match中匹配了，也要深入递归对比内部结构
            for orig_idx, curr_idx in origin_matched.items():
                elem_path = f"{path}[{orig_idx}]"
                if _should_exclude(elem_path, exclude_fields):
                    continue

                origin_item = origin_list_copy[orig_idx]
                current_item = current_list_copy[curr_idx]

                # 优化：对于复杂类型（dict/list），总是进行递归对比，即使_items_match返回True
                # 这样可以检测到内部字段的细微差异
                if isinstance(origin_item, (dict, list)) and isinstance(current_item, (dict, list)):
                    differences += compare_structures(
                        origin_item,
                        current_item,
                        elem_path,
                        True,  # check_value
                        True,  # check_missing
                        False,  # check_redundant
                        check_type,
                        exclude_fields,
                        deep_diff_contrast_config,
                        open_log,
                    )
                elif isinstance(origin_item, dict) or isinstance(current_item, dict):
                    # 如果一个是dict另一个不是，说明类型不匹配
                    if check_type:
                        differences.append(
                            f"[类型冲突] {elem_path} "
                            f"Origin类型：{_type_detail(origin_item)} → "
                            f"Current类型：{_type_detail(current_item)}"
                        )
                elif isinstance(origin_item, list) or isinstance(current_item, list):
                    # 如果一个是list另一个不是，说明类型不匹配
                    if check_type:
                        differences.append(
                            f"[类型冲突] {elem_path} "
                            f"Origin类型：{_type_detail(origin_item)} → "
                            f"Current类型：{_type_detail(current_item)}"
                        )
                else:
                    # 基础类型对比
                    # 第一步：检查等价值（优先于类型检查，需要配置 ignore_type_in_groups）
                    if _is_equivalent_value(origin_item, current_item, deep_diff_contrast_config):
                        continue  # 跳过差异记录

                    # 第二步：类型冲突检查
                    if check_type and not _is_same_type(origin_item, current_item, deep_diff_contrast_config):
                        differences.append(
                            f"[类型冲突] {elem_path} "
                            f"Origin类型：{_type_detail(origin_item)} → "
                            f"Current类型：{_type_detail(current_item)}"
                        )
                    elif origin_item != current_item:
                        # 检查类型转换
                        if deep_diff_contrast_config.get("ignore_type_in_groups"):
                            skip = _type_conversion_judgment(origin_item, current_item, deep_diff_contrast_config)
                            if skip:
                                continue
                        old_formatted = _format_structure(origin_item)
                        new_formatted = _format_structure(current_item)
                        differences.append(
                            f"[值变化] {elem_path} Origin值: {old_formatted} → Current值: {new_formatted}"
                        )
        else:
            # 不忽略顺序，按索引对比
            max_len = max(len(origin_list), len(current_list))
            for i in range(max_len):
                elem_path = f"{path}[{i}]"

                # 检查是否在排除字段中
                if _should_exclude(elem_path, exclude_fields):
                    continue

                if i >= len(origin_list):
                    differences.append(
                        f"[列表差异] {elem_path} (iterable_item_added)"
                    )
                    continue

                if i >= len(current_list):
                    differences.append(
                        f"[列表差异] {elem_path} (iterable_item_removed)"
                    )
                    continue

                origin_item = origin_list[i]
                current_item = current_list[i]

                # 递归对比
                if isinstance(origin_item, (dict, list)) and isinstance(current_item, (dict, list)):
                    differences += compare_structures(
                        origin_item,
                        current_item,
                        elem_path,
                        True,  # check_value
                        True,  # check_missing
                        False,  # check_redundant
                        check_type,
                        exclude_fields,
                        deep_diff_contrast_config,
                        open_log,
                    )
                else:
                    # 基础类型对比
                    # 第一步：检查等价值（优先于类型检查，需要配置 ignore_type_in_groups）
                    if _is_equivalent_value(origin_item, current_item, deep_diff_contrast_config):
                        continue  # 跳过差异记录

                    # 第二步：类型冲突检查
                    if check_type and not _is_same_type(origin_item, current_item, deep_diff_contrast_config):
                        differences.append(
                            f"[类型冲突] {elem_path} "
                            f"Origin类型：{_type_detail(origin_item)} → "
                            f"Current类型：{_type_detail(current_item)}"
                        )
                    elif origin_item != current_item:
                        # 检查类型转换
                        if deep_diff_contrast_config.get("ignore_type_in_groups"):
                            skip = _type_conversion_judgment(origin_item, current_item, deep_diff_contrast_config)
                            if skip:
                                continue
                        old_formatted = _format_structure(origin_item)
                        new_formatted = _format_structure(current_item)
                        differences.append(
                            f"[值变化] {elem_path} Origin值: {old_formatted} → Current值: {new_formatted}"
                        )

        return differences

    def _items_match(
        origin_item: Any,
        current_item: Any,
        check_type: bool,
        deep_diff_contrast_config: Dict,
    ) -> bool:
        """
        判断两个列表元素是否匹配（用于忽略顺序的列表对比）
        """
        # 类型检查
        if check_type and not _is_same_type(origin_item, current_item, deep_diff_contrast_config):
            return False

        # 基本类型直接比较
        if not isinstance(origin_item, (dict, list)) and not isinstance(current_item, (dict, list)):
            # 检查类型转换
            if deep_diff_contrast_config.get("ignore_type_in_groups"):
                if _type_conversion_judgment(origin_item, current_item, deep_diff_contrast_config):
                    return True
            return origin_item == current_item

        # 复杂类型需要深度比较
        if isinstance(origin_item, dict) and isinstance(current_item, dict):
            if len(origin_item) != len(current_item):
                return False
            for key in origin_item:
                if key not in current_item:
                    return False
                if not _items_match(origin_item[key], current_item[key], check_type, deep_diff_contrast_config):
                    return False
            return True

        if isinstance(origin_item, list) and isinstance(current_item, list):
            if len(origin_item) != len(current_item):
                return False
            # 对于列表，递归比较每个元素
            for orig_elem, curr_elem in zip(origin_item, current_item):
                if not _items_match(orig_elem, curr_elem, check_type, deep_diff_contrast_config):
                    return False
            return True

        return False

    def _should_exclude(clean_path: str, exclude_fields: Set[str]) -> bool:
        """
        判断给定的路径是否需要被排除，支持多层结构和通配符 [*] 的匹配。

        参数:
        clean_path (str): 待检查的路径字符串，可能是多层级结构，如 "users.series.title"。
        exclude_fields (set): 包含需要排除的字段的集合，部分字段可能带有通配符 [*]，
                              例如 "list[*].interest_tag[*].add_time"。

        返回:
        bool: 如果 clean_path 匹配到 exclude_fields 中的某个字段，则返回 True；否则返回 False。
        """
        # 将 clean_path 按点号分割成多个部分，用于后续逐部分匹配
        clean_parts = clean_path.split(".")
        # 遍历排除字段集合中的每个字段
        for field in exclude_fields:
            # 将当前排除字段按点号分割成多个部分
            field_parts = field.split(".")
            # 若排除字段的部分数量少于 clean_path 的部分数量，无法匹配，跳过该字段
            if len(field_parts) < len(clean_parts):
                continue
            # 初始化匹配标志为 True
            match = True
            # 逐部分比较 clean_path 和当前排除字段
            for i, part in enumerate(field_parts):
                # 若已遍历完 clean_path 的所有部分，跳出循环
                if i >= len(clean_parts):
                    break
                # 检查当前部分是否以 [*] 结尾，若是则表示使用了通配符
                if part.endswith("[*]"):
                    # 提取 [*] 之前的基础部分
                    base = part[:-3]
                    # 若 clean_path 对应部分与基础部分不匹配，标记为不匹配
                    if clean_parts[i] != base:
                        match = False
                        break
                # 若当前部分不以 [*] 结尾，直接检查是否与 clean_path 对应部分不匹配
                elif part != clean_parts[i]:
                    match = False
                    break
            # 若所有部分都匹配，返回 True
            if match:
                return True
        # 若遍历完所有排除字段都未匹配，返回 False
        return False

    def _type_conversion_judgment(old_value: Any, new_value: Any, deep_diff_contrast_config: Dict) -> bool:
        """
        类型转换判断逻辑

        Returns:
            bool: 如果应该跳过类型检查返回 True，否则返回 False
        """
        type_groups = deep_diff_contrast_config.get("ignore_type_in_groups", [])
        if not type_groups:
            return False

        old_type = type(old_value)
        new_type = type(new_value)

        # 如果类型相同，不需要转换判断
        if old_type == new_type:
            return False

        for group in type_groups:
            if old_type in group and new_type in group:
                try:
                    # 尝试转换为相同类型后比较
                    if old_type == str:
                        return old_value == str(new_value)
                    elif old_type == int:
                        return old_value == int(new_value)
                    elif old_type == float:
                        return old_value == float(new_value)
                    elif new_type == str:
                        return str(old_value) == new_value
                    elif new_type == int:
                        return int(old_value) == new_value
                    elif new_type == float:
                        return float(old_value) == new_value
                except (ValueError, TypeError):
                    continue

        return False  # 默认返回 False

    def _special_value_check(
        origin_val: Any, current_val: Any, path: str, differences: List[str]
    ) -> List[str]:
        """统一特殊值检查函数"""
        # 类型分流检查
        if isinstance(origin_val, str) and isinstance(current_val, str):
            # 字符串空值检查
            if origin_val.strip() != "" and current_val.strip() == "":
                differences.append(
                    f"[值变化] {path} "
                    f"Origin值: '{_truncate(origin_val, 30)}' → "
                    f"Current值: '{_truncate(current_val, 30)}' (空值警告)"
                )

        elif isinstance(origin_val, int) and isinstance(current_val, int):
            # 整数值合法性检查
            if origin_val != current_val and current_val <= 0:
                differences.append(
                    f"[值变化] {path} "
                    f"Origin值: {origin_val} → "
                    f"Current值: {current_val} (负数/零警告)"
                )

        return differences


    def _is_equivalent_value(origin_val: Any, current_val: Any, deep_diff_contrast_config: Dict) -> bool:
        """
        独立等价判断逻辑
        只有当 deep_diff_contrast_config.ignore_type_in_groups 配置了相应类型组时才启用等价值判断
        """
        # 如果没有配置 ignore_type_in_groups，则不进行等价值判断
        type_groups = deep_diff_contrast_config.get("ignore_type_in_groups", []) if deep_diff_contrast_config else []
        if not type_groups or len(type_groups) == 0:
            return False

        # 检查类型是否在配置的类型组中
        origin_type = type(origin_val)
        current_type = type(current_val)

        # 判断两个类型是否在同一个类型组中
        types_in_same_group = False
        for group in type_groups:
            if not isinstance(group, (list, tuple)):
                continue

            # 检查类型是否在组中
            origin_in_group = origin_type in group
            current_in_group = current_type in group

            if origin_in_group and current_in_group:
                types_in_same_group = True
                break

        # 如果类型不在同一个类型组中，不进行等价值判断
        if not types_in_same_group:
            return False

        # 空字符串与0等价（需要配置了 number 和 string 类型组）
        if (origin_val == "" and current_val == 0) or (
            origin_val == 0 and current_val == ""
        ):
            return True

        # 数字字符串与数字等价
        if (
            isinstance(origin_val, str)
            and origin_val.isdigit()
            and isinstance(current_val, (int, float))
        ):
            return int(origin_val) == current_val
        if (
            isinstance(current_val, str)
            and current_val.isdigit()
            and isinstance(origin_val, (int, float))
        ):
            return int(current_val) == origin_val

        # 浮点数字符串与数字等价
        if isinstance(origin_val, str) and isinstance(current_val, (int, float)):
            try:
                return float(origin_val) == float(current_val)
            except (ValueError, TypeError):
                pass
        if isinstance(current_val, str) and isinstance(origin_val, (int, float)):
            try:
                return float(current_val) == float(origin_val)
            except (ValueError, TypeError):
                pass

        # 浮点数与整数等价（值相等时）
        if isinstance(origin_val, float) and isinstance(current_val, int):
            return origin_val == float(current_val)
        if isinstance(origin_val, int) and isinstance(current_val, float):
            return float(origin_val) == current_val

        return False

    def _is_same_type(origin_val: Any, current_val: Any, config: Dict) -> bool:
        """仅处理类型组配置"""
        type_groups = config.get("ignore_type_in_groups", [])
        for group in type_groups:
            if (type(origin_val) in group) and (type(current_val) in group):
                return True
        return type(origin_val) is type(current_val)

    def _format_path(raw_path: str) -> str:
        """标准化路径格式：将 ['0'] 转换为"""
        return re.sub(r"\[\'(\d+)\'\]", r"[\1]", raw_path)

    def _type_detail(obj: Any) -> str:
        """增强类型描述"""
        if obj is None:
            return "null"
        if isinstance(obj, bool):
            return "bool"
        if isinstance(obj, (int, float)):
            return f"{type(obj).__name__}({obj})"
        if isinstance(obj, str):
            return f"str('{_truncate(obj)}')" if obj else "str(空)"
        if isinstance(obj, list):
            return f"list[{len(obj)}]"
        if isinstance(obj, dict):
            return f"dict[{len(obj)}]"
        return type(obj).__name__

    def _format_value(value: Any) -> str:
        """仅格式化单个值，不修改容器结构"""
        if isinstance(value, str):
            if value == "":
                return "'' → (等价0)"
            if value.isdigit():
                return f"'{value}' → ({int(value)})"
            return f"'{value}'"

        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, (int, float)):
            return f"{value} → (等价'{value}')" if value == 0 else str(value)

        return str(value)

    def _format_structure(data: Any) -> Any:
        """安全遍历数据结构并格式化"""
        if not isinstance(data, (dict, list, str, int, float, bool)):
            return str(data)  # 处理不可序列化对象
        if isinstance(data, dict):
            return {k: _format_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_format_structure(e) for e in data]
        else:
            # 仅叶子节点被格式化
            return _format_value(data)

    def _truncate(s: str, max_len: int = 50) -> str:
        """字符串截断"""
        return s[:max_len] + "..." if len(s) > max_len else s

    # 主函数逻辑开始
    differences = []
    exclude_fields = exclude_fields or {"go_article_service"}
    deep_diff_contrast_config = deep_diff_contrast_config or {
        # 忽略对比列表顺序
        "ignore_order": True,
        # 忽略类型不一致
        # 'ignore_type_in_groups': [(int, str, float, bool)],
    }

    origin_data = deepcopy(origin_data)
    current_data = deepcopy(current_data)

    # 判断是否是第一次进入函数
    if not path:
        # 检查origin_data和current_data是否为字典和列表类型
        if not isinstance(origin_data, (dict, list)) or not isinstance(
            current_data, (dict, list)
        ):
            raise ValueError("Origin和Current数据必须是字典或列表类型")

    # 处理null值特殊情况
    if origin_data is None and current_data is None:
        return differences
    if origin_data is None:
        if check_missing:
            differences.append(f"[字段缺失] {path} (Origin类型: null)")
        return differences
    if current_data is None:
        if check_redundant:
            differences.append(f"[冗余字段] {path} (Current类型: null)")
        return differences

    # 主对比逻辑
    if isinstance(origin_data, dict) and isinstance(current_data, dict):
        return _compare_dicts(
            origin_data,
            current_data,
            path,
            check_value,
            check_missing,
            check_redundant,
            check_type,
            exclude_fields,
            deep_diff_contrast_config,
            differences,
            open_log,
        )
    elif isinstance(origin_data, list) and isinstance(current_data, list):
        return _compare_lists(
            origin_data,
            current_data,
            path,
            check_value,
            check_missing,
            check_redundant,
            check_type,
            exclude_fields,
            deep_diff_contrast_config,
            differences,
            open_log,
        )
    else:
        # origin_data和current_data类型不一致
        if check_type and not _is_same_type(
            origin_data, current_data, deep_diff_contrast_config
        ):
            differences.append(
                f"[类型冲突] {path} "
                f"Origin类型: {_type_detail(origin_data)} → "
                f"Current类型: {_type_detail(current_data)}"
            )
    return differences


def main():
    """
    主函数：处理输入参数并执行核心逻辑 并返回结果 结果为json格式
    参数：
    - origin_data: 原始数据 字典格式
    - current_data: 当前数据 字典格式
    - check_value: 是否检查值差异 布尔值 (可选，默认True)
    - check_missing: 是否检查缺失字段 布尔值 (可选，默认True)
    - check_redundant: 是否检查冗余字段 布尔值 (可选，默认False)
    - check_type: 是否检查类型差异 布尔值 (可选，默认True)
    - exclude_fields: 排除字段 列表格式，会被转换为集合 (可选，默认None)
    - deep_diff_contrast_config: 对比配置 字典格式 (可选，默认None)
    - open_log: 是否开启日志 布尔值 (可选，默认False)
    - path: 当前路径 字符串 (可选，默认"")

    返回：JSON格式字符串，包含差异列表
    """
    try:
        # 从命令行参数获取JSON字符串
        if len(sys.argv) > 1:
            input_json = sys.argv[1]
            params = json.loads(input_json)
        else:
            # 如果没有参数，返回错误信息
            result = {
                "success": False,
                "error": "缺少输入参数，需要传入JSON格式的参数",
                "differences": []
            }
            print(json.dumps(result, ensure_ascii=False))
            return

        # 提取必需参数
        origin_data = params.get("origin_data")
        current_data = params.get("current_data")

        if origin_data is None or current_data is None:
            result = {
                "success": False,
                "error": "缺少必需参数：origin_data 和 current_data",
                "differences": []
            }
            print(json.dumps(result, ensure_ascii=False))
            return

        # 提取可选参数并设置默认值
        check_value = params.get("check_value", True)
        check_missing = params.get("check_missing", True)
        check_redundant = params.get("check_redundant", False)
        check_type = params.get("check_type", True)
        exclude_fields = params.get("exclude_fields")
        deep_diff_contrast_config = params.get("deep_diff_contrast_config")
        open_log = params.get("open_log", False)
        path = params.get("path", "")

        # 类型转换：exclude_fields 从列表转换为集合
        if exclude_fields is not None:
            if isinstance(exclude_fields, list):
                exclude_fields = set(exclude_fields)
            elif isinstance(exclude_fields, set):
                pass  # 已经是集合，无需转换
            else:
                exclude_fields = set([exclude_fields])  # 单个字符串转换为集合

        # 调用 compare_structures 函数
        differences = compare_structures(
            origin_data=origin_data,
            current_data=current_data,
            path=path,
            check_value=check_value,
            check_missing=check_missing,
            check_redundant=check_redundant,
            check_type=check_type,
            exclude_fields=exclude_fields,
            deep_diff_contrast_config=deep_diff_contrast_config,
            open_log=open_log,
        )

        # 构建返回结果
        result = {
            "success": True,
            "differences": differences,
            "difference_count": len(differences),
            "is_identical": len(differences) == 0
        }

        # 输出JSON格式结果（Apifox会读取标准输出）
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "error": f"JSON解析错误: {str(e)}",
            "differences": []
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        result = {
            "success": False,
            "error": f"执行错误: {str(e)}",
            "differences": []
        }
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
