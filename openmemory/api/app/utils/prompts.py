MEMORY_CATEGORIZATION_PROMPT = """你的任务是将每条信息（或"记忆"）分配到一个或多个以下类别。可以根据需要为每条信息分配多个类别。

- 个人：家庭、朋友、家居、爱好、生活方式
- 人际关系：社交网络、伴侣、同事
- 偏好：喜好、厌恶、习惯、喜爱的媒体
- 健康：身体健康、心理健康、饮食、睡眠
- 旅行：旅行、通勤、喜爱的地点、行程
- 工作：工作角色、公司、项目、晋升
- 教育：课程、学位、证书、技能发展
- 项目：待办事项、里程碑、截止日期、状态更新
- AI、ML与技术：基础设施、算法、工具、研究
- 技术支持：错误报告、错误日志、修复方案
- 财务：收入、支出、投资、账单
- 购物：购买、愿望清单、退货、配送
- 法律：合同、政策、法规、隐私
- 娱乐：电影、音乐、游戏、书籍、活动
- 消息：电子邮件、短信、提醒
- 客户支持：工单、咨询、解决方案
- 产品反馈：评分、错误报告、功能请求
- 新闻：文章、头条、热门话题
- 组织：会议、约会、日程表
- 目标：抱负、KPI、长期目标

指南：
- 你必须严格返回有效的JSON格式，不包含任何前导或后缀文本
- 你的响应必须是一个包含'categories'键的JSON对象，值为类别字符串数组
- 例如：{"categories": ["personal", "relationships"]}
- 所有返回的类别名称必须使用英文，即使内容是中文的
- 如果无法对记忆进行分类，请返回带有'categories'键的空列表：{"categories": []}
- 不要仅限于上面列出的类别。可以根据记忆内容创建新类别。确保它是单个短语

记住，你的整个输出必须只是一个有效的JSON对象，没有任何额外的文本、解释或装饰。
"""

# MEMORY_CATEGORIZATION_PROMPT = """Your task is to assign each piece of information (or “memory”) to one or more of the following categories. Feel free to use multiple categories per item when appropriate.
#
# - Personal: family, friends, home, hobbies, lifestyle
# - Relationships: social network, significant others, colleagues
# - Preferences: likes, dislikes, habits, favorite media
# - Health: physical fitness, mental health, diet, sleep
# - Travel: trips, commutes, favorite places, itineraries
# - Work: job roles, companies, projects, promotions
# - Education: courses, degrees, certifications, skills development
# - Projects: to‑dos, milestones, deadlines, status updates
# - AI, ML & Technology: infrastructure, algorithms, tools, research
# - Technical Support: bug reports, error logs, fixes
# - Finance: income, expenses, investments, billing
# - Shopping: purchases, wishlists, returns, deliveries
# - Legal: contracts, policies, regulations, privacy
# - Entertainment: movies, music, games, books, events
# - Messages: emails, SMS, alerts, reminders
# - Customer Support: tickets, inquiries, resolutions
# - Product Feedback: ratings, bug reports, feature requests
# - News: articles, headlines, trending topics
# - Organization: meetings, appointments, calendars
# - Goals: ambitions, KPIs, long‑term objectives
#
# Guidelines:
# - Return only the categories under 'categories' key in the JSON format.
# - If you cannot categorize the memory, return an empty list with key 'categories'.
# - Don't limit yourself to the categories listed above only. Feel free to create new categories based on the memory. Make sure that it is a single phrase.
# """
