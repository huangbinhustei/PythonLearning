## 已经完成
1. 数据获取
2. 去重
3. 数据库 vacuum
4. 数据库索引：
	- 方法一：对于这种，似乎索引中的第一个（grade）必须用，否则不会使用索引。
		- create index list_index ON docs (grade, genre, words);
	- 方法二：对于这种，似乎索引都能够用上，但是比较慢。
		- CREATE INDEX grade_index ON docs (grade);
		- CREATE INDEX genre_index ON docs (genre);
		- CREATE INDEX words_index ON docs (words);
5. 用『.schema』可以看结构

## 待办事项
1. 数据清洗：
	1. 去掉干扰信息（目前来看干扰数据正好用作分段落）。
	2. 年级、体裁改成枚举值。
	3. 导入默认的阅读次数
2. 获取标签数据（倒查表？）和相关推荐。
3. slugify
4. 页面分工：
	1. Layout：网站标题、CSS 继承、（页面左右分区？）
	2. View：
		1. 标题、作者、访问量、正文、年级、字数、体裁
		2. URLs：同标题作文、Tag、相关推荐、再来一篇
	3. List：
		1. 标题、年级、体裁、字数、摘要、URL
		2. 分页
		3. 筛选：年级、字数、体裁

## table
docs：	doc_id url title content grade genre words tags author view yesterday_view today_view creat_time upgrade_tiem fromer_url former_organization
tags：	tag_id doc_ids
sug：	id title doc_ids

首页：		按照最近一周的热度降序排列。昨日PV*0.7 + 今日PV*0.3。
标题列表页：	select doc_id from composition where title is "标题"
tag列表页：	list = [item.split(",") for item in select doc_ids from composition where tag_id is "id"]
搜索结果页：