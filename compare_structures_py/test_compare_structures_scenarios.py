#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_structures 函数功能验证测试脚本

测试各种场景，确保函数功能正常
"""
import sys
import json
import os
from compare_structures import compare_structures


def test_scenario(name: str, origin_data, current_data, **kwargs):
    """测试场景辅助函数"""
    print(f"\n{'='*60}")
    print(f"测试场景: {name}")
    print(f"{'='*60}")
    print(f"原始数据: {origin_data}")
    print(f"当前数据: {current_data}")
    if kwargs:
        print(f"配置参数: {kwargs}")

    diffs = compare_structures(origin_data, current_data, **kwargs)

    if not diffs:
        print("✅ 结果: 数据完全一致")
    else:
        print(f"❌ 结果: 发现 {len(diffs)} 处差异:")
        for i, diff in enumerate(diffs, 1):
            print(f"  {i}. {diff}")

    return diffs


def main():
    """主测试函数"""
    print("=" * 60)
    print("compare_structures 函数功能验证测试")
    print("=" * 60)

    all_passed = True

    # ========== 场景 1: 简单对象对比 ==========
    try:
        origin = {"name": "张三", "age": 25, "city": "北京"}
        current = {"name": "张三", "age": 26, "city": "北京"}
        diffs = test_scenario("场景1: 简单对象对比", origin, current)
        expected = 1  # 应该检测到 age 字段的值变化
        if len(diffs) != expected:
            print(f"⚠️  预期 {expected} 处差异，实际 {len(diffs)} 处")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 2: 检测缺失字段 ==========
    try:
        origin = {"name": "张三", "age": 25, "email": "zhang@example.com"}
        current = {"name": "张三", "age": 25}
        diffs = test_scenario("场景2: 检测缺失字段", origin, current)
        expected = 1  # 应该检测到 email 字段缺失
        if len(diffs) != expected or "[字段缺失]" not in diffs[0]:
            print(f"⚠️  预期检测到字段缺失，但结果不符合预期")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 3: 检测类型冲突 ==========
    try:
        origin = {"count": 100}
        current = {"count": "100"}
        diffs = test_scenario("场景3: 检测类型冲突", origin, current, check_type=True)
        expected = 1  # 应该检测到类型冲突
        if len(diffs) != expected or "[类型冲突]" not in diffs[0]:
            print(f"⚠️  预期检测到类型冲突，但结果不符合预期")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 4: 检测冗余字段 ==========
    try:
        origin = {"name": "张三", "age": 25}
        current = {"name": "张三", "age": 25, "email": "zhang@example.com"}
        diffs = test_scenario(
            "场景4: 检测冗余字段", origin, current, check_redundant=True
        )
        expected = 1  # 应该检测到冗余字段
        if len(diffs) != expected or "[冗余字段]" not in diffs[0]:
            print(f"⚠️  预期检测到冗余字段，但结果不符合预期")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 5: 排除特定字段 ==========
    try:
        origin = {"name": "张三", "timestamp": 1234567890, "data": {"value": 100}}
        current = {"name": "李四", "timestamp": 1234567891, "data": {"value": 100}}
        diffs = test_scenario(
            "场景5: 排除特定字段", origin, current, exclude_fields={"timestamp"}
        )
        # 应该只检测到 name 的变化，timestamp 被排除
        if any("timestamp" in diff for diff in diffs):
            print(f"⚠️  排除字段 timestamp 仍然被检测到")
            all_passed = False
        if not any("name" in diff for diff in diffs):
            print(f"⚠️  应该检测到 name 字段的变化")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 6: 排除嵌套字段 ==========
    try:
        origin = {
            "user": {
                "name": "张三",
                "profile": {"avatar": "avatar1.jpg", "settings": {"theme": "dark"}},
            }
        }
        current = {
            "user": {
                "name": "张三",
                "profile": {"avatar": "avatar2.jpg", "settings": {"theme": "light"}},
            }
        }
        diffs = test_scenario(
            "场景6: 排除嵌套字段", origin, current, exclude_fields={"user.profile"}
        )
        # profile 及其所有子字段都应该被排除
        if any(
            "profile" in diff or "avatar" in diff or "settings" in diff
            for diff in diffs
        ):
            print(f"⚠️  排除字段 user.profile 仍然被检测到")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 7: 使用通配符排除列表字段 ==========
    try:
        origin = {
            "rows": [
                {"id": 1, "link": "http://example.com/1", "title": "标题1"},
                {"id": 2, "link": "http://example.com/2", "title": "标题2"},
            ]
        }
        current = {
            "rows": [
                {"id": 1, "link": "http://example.com/1-new", "title": "标题1"},
                {"id": 2, "link": "http://example.com/2-new", "title": "标题2"},
            ]
        }
        diffs = test_scenario(
            "场景7: 使用通配符排除列表字段",
            origin,
            current,
            exclude_fields={"rows[*].link"},
        )
        # link 字段的差异应该被忽略
        if any("link" in diff for diff in diffs):
            print(f"⚠️  排除字段 rows[*].link 仍然被检测到")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 8: 有序列表对比（按索引） ==========
    try:
        origin = {"items": [{"id": 1, "name": "第一项"}, {"id": 2, "name": "第二项"}]}
        current = {"items": [{"id": 2, "name": "第二项"}, {"id": 1, "name": "第一项"}]}
        diffs = test_scenario(
            "场景8: 有序列表对比（按索引）",
            origin,
            current,
            deep_diff_contrast_config={"ignore_order": False},
        )
        # 按索引对比应该检测到差异
        if len(diffs) == 0:
            print(f"⚠️  按索引对比应该检测到差异，但未检测到")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 9: 无序列表对比（忽略顺序） ==========
    try:
        origin = {"tags": ["tag1", "tag2", "tag3"]}
        current = {"tags": ["tag3", "tag1", "tag2"]}
        diffs = test_scenario(
            "场景9: 无序列表对比（忽略顺序）",
            origin,
            current,
            deep_diff_contrast_config={"ignore_order": True},
        )
        # 忽略顺序应该不检测到差异
        if len(diffs) > 0:
            print(f"⚠️  忽略顺序时不应该检测到差异，但检测到了 {len(diffs)} 处")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 10: 复杂嵌套结构对比 ==========
    try:
        origin = {
            "users": [
                {
                    "id": 1,
                    "name": "张三",
                    "orders": [
                        {"orderId": "001", "amount": 100},
                        {"orderId": "002", "amount": 200},
                    ],
                }
            ]
        }
        current = {
            "users": [
                {
                    "id": 1,
                    "name": "张三",
                    "orders": [
                        {"orderId": "001", "amount": 150},
                        {"orderId": "002", "amount": 200},
                    ],
                }
            ]
        }
        # 使用 ignore_order=False 确保按索引对比，能检测到内部差异
        diffs = test_scenario(
            "场景10: 复杂嵌套结构对比",
            origin,
            current,
            deep_diff_contrast_config={"ignore_order": False},
        )
        # 应该检测到 amount 的变化
        if not any("amount" in diff for diff in diffs):
            print(f"⚠️  应该检测到 amount 字段的变化")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 11: 类型组配置（允许类型转换） ==========
    try:
        origin = {"count": "100"}
        current = {"count": 100}
        diffs = test_scenario(
            "场景11: 类型组配置（允许类型转换）",
            origin,
            current,
            deep_diff_contrast_config={"ignore_type_in_groups": [(int, str)]},
        )
        # 如果类型转换成功，不应该报告类型冲突
        if any("[类型冲突]" in diff for diff in diffs):
            print(f"⚠️  配置了类型组后不应该报告类型冲突")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 12: 只检查结构，不检查值 ==========
    try:
        origin = {"name": "张三", "age": 25}
        current = {"name": "李四", "age": 30}
        diffs = test_scenario(
            "场景12: 只检查结构，不检查值", origin, current, check_value=False
        )
        # 不检查值，应该没有差异
        if len(diffs) > 0:
            print(f"⚠️  不检查值时不应该有差异，但检测到了 {len(diffs)} 处")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 13: 只检查值，不检查类型 ==========
    try:
        origin = {"count": 100}
        current = {"count": "100"}
        diffs = test_scenario(
            "场景13: 只检查值，不检查类型",
            origin,
            current,
            check_type=False,
            deep_diff_contrast_config={"ignore_type_in_groups": [(int, str)]},
        )
        # 不检查类型，值相同，应该没有差异
        if len(diffs) > 0:
            print(f"⚠️  不检查类型且值相同时不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 14: 空值处理 ==========
    try:
        origin = {"field": None}
        current = {"field": None}
        diffs = test_scenario("场景14: 空值处理", origin, current)
        # 两个都是 None，应该没有差异
        if len(diffs) > 0:
            print(f"⚠️  两个 None 值不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 15: 等价值判断 ==========
    try:
        origin = {"value": ""}
        current = {"value": 0}
        diffs = test_scenario(
            "场景15: 等价值判断（空字符串与0）",
            origin,
            current,
            deep_diff_contrast_config={"ignore_type_in_groups": [(str, int)]},
        )
        # 空字符串和0应该等价，不应该有差异
        if len(diffs) > 0:
            print(f"⚠️  空字符串和0应该等价，不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 16: 数字字符串与数字等价 ==========
    try:
        origin = {"count": "100"}
        current = {"count": 100}
        diffs = test_scenario(
            "场景16: 数字字符串与数字等价",
            origin,
            current,
            deep_diff_contrast_config={"ignore_type_in_groups": [(str, int)]},
        )
        # 数字字符串和数字应该等价，不应该有差异
        if len(diffs) > 0:
            print(f"⚠️  数字字符串和数字应该等价，不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 17: 列表长度差异 ==========
    try:
        origin = {"items": [1, 2, 3]}
        current = {"items": [1, 2]}
        diffs = test_scenario("场景17: 列表长度差异", origin, current)
        # 应该检测到列表长度差异
        if len(diffs) == 0:
            print(f"⚠️  应该检测到列表长度差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 18: 开启日志调试 ==========
    try:
        origin = {"items": [1, 2, 3]}
        current = {"items": [3, 1, 2]}
        print("\n" + "=" * 60)
        print("场景18: 开启日志调试")
        print("=" * 60)
        diffs = test_scenario(
            "场景18: 开启日志调试",
            origin,
            current,
            deep_diff_contrast_config={"ignore_order": True},
            open_log=True,
        )
        # 应该输出日志
        print("✅ 日志已输出（请查看上方日志信息）")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 19: 使用真实JSON数据对比 ==========
    try:
        # 获取JSON文件路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        php_data_path = os.path.join(project_root, "parameters", "php_data.json")
        go_data_path = os.path.join(project_root, "parameters", "go_data.json")

        if os.path.exists(php_data_path) and os.path.exists(go_data_path):
            with open(php_data_path, "r", encoding="utf-8") as f:
                php_data = json.load(f)
            with open(go_data_path, "r", encoding="utf-8") as f:
                go_data = json.load(f)

            print("\n" + "=" * 60)
            print("场景19: 使用真实JSON数据对比")
            print("=" * 60)
            print(f"PHP数据文件: {php_data_path}")
            print(f"Go数据文件: {go_data_path}")

            # 对比data字段
            diffs = test_scenario(
                "场景19: 真实JSON数据对比（排除链接字段）",
                php_data.get("data", {}),
                go_data.get("data", {}),
                exclude_fields={
                    "rows[*].buy_steps[*].sub_rows[*].link",
                    "rows[*].buy_steps[*].sub_rows[*].redirect_data.link",
                    "rows[*].buy_steps[*].sub_rows[*].redirect_data.link_val",
                    "rows[*].buy_steps[*].sub_rows[*].redirect_data.md5_url",
                    "rows[*].buy_steps[*].sub_rows[*].redirect_data.sdk_link",
                },
                open_log=False,
            )

            if len(diffs) == 0:
                print("✅ 真实数据对比：排除链接字段后数据完全一致")
            else:
                print(f"⚠️  真实数据对比：发现 {len(diffs)} 处差异（排除链接字段后）")
                # 只显示前5个差异
                for i, diff in enumerate(diffs[:5], 1):
                    print(f"  {i}. {diff}")
                if len(diffs) > 5:
                    print(f"  ... 还有 {len(diffs) - 5} 处差异未显示")
        else:
            print("\n" + "=" * 60)
            print("场景19: 使用真实JSON数据对比")
            print("=" * 60)
            print(f"⚠️  JSON文件不存在，跳过此测试")
            print(f"  预期路径: {php_data_path}")
            print(f"  预期路径: {go_data_path}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        all_passed = False

    # ========== 场景 20: 浮点数与整数等价判断 ==========
    try:
        origin = {"value": 100.0}
        current = {"value": 100}
        diffs = test_scenario(
            "场景20: 浮点数与整数等价判断",
            origin,
            current,
            deep_diff_contrast_config={"ignore_type_in_groups": [(float, int)]},
        )
        # 浮点数100.0和整数100应该等价
        if len(diffs) > 0:
            print(f"⚠️  浮点数100.0和整数100应该等价，不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 场景 21: 浮点数字符串与数字等价 ==========
    try:
        origin = {"value": "100.5"}
        current = {"value": 100.5}
        diffs = test_scenario(
            "场景21: 浮点数字符串与数字等价",
            origin,
            current,
            deep_diff_contrast_config={"ignore_type_in_groups": [(str, float)]},
        )
        # 浮点数字符串"100.5"和浮点数100.5应该等价
        if len(diffs) > 0:
            print(f"⚠️  浮点数字符串和浮点数应该等价，不应该有差异")
            all_passed = False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        all_passed = False

    # ========== 总结 ==========
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试场景验证完成！")
    else:
        print("⚠️  部分测试场景可能存在问题，请检查上述输出")
    print("=" * 60)


if __name__ == "__main__":
    main()
