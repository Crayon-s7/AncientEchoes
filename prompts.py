chapter_classifier_prompt = """请根据以下规则判断章节是否包含实际内容，并输出"true"或"false"。

章节名称中包含以下关键词的，视为不包含实际内容，输出"false"：
- 书名页
- 目录
- 前言
- 附录
- 索引
- 译注说明
- 上册
- 下册

其他章节名称视为包含实际内容，输出"true"。

# Steps

1. 检查章节名称是否包含上述关键词。
2. 如果包含，输出"false"。
3. 如果不包含，输出"true"。

# Output Format

输出为单个字符串，值为"true"或"false"。

# Examples

输入：书名页
输出：false

输入：前言
输出：false

输入：隐公
输出：true

输入：庄公
输出：true

输入：上册
输出：false

输入：下册
输出：false

# Notes

确保章节名称完全匹配关键词，不考虑部分匹配或拼写错误。"""


is_chinese_prompt = """判断给定的文字是文言文还是白话文，并以JSON格式输出结果。

# 输出格式

输出应为一个JSON对象，包含一个键值对。键为`result`，值为`'文言文'`或`'白话文'`。

# 示例

输入: "吾日三省吾身"
输出: {"result": "文言文"}

输入: "我每天反省自己三次"
输出: {"result": "白话文"}

输入: "元年者何？君之始年也。春者何？岁之始也。王者孰谓？谓文王也。曷为先言王而后言正月？王正月也。何言乎王正月？大一统也。公何以不言即位？成公意也。何成乎公之意？公将平国而反之桓。曷为反之桓？桓幼而贵，隐长而卑。其为尊卑也微，国人莫知"
输出: {"result": "文言文"}
"""
