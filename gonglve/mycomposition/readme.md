## 已经完成
1. 数据相关：
   + 获取数据（抓取 or 导入），将年级、体裁做成数字。
   + slugify：用标题的拼音作为 url 参数。
   + 数据去重。
   + 将正文中的作者、学校信息，提炼成机构和作者字段：这个部分完成。
   + 有些内容，段前空格是放在正文里面的，批量去掉，用 indent 处理段首空格。
2. 通用：统计每个函数的耗时。
3. 阅读页：
   + 展示信息和正文。
   + 能计算阅读量。
4. 列表页：
   + 分页展示信息和摘要（摘要的处理方法有点 low）
   + 假如 URL 里面带了参数，能够进行针对的筛选（但是还不会在前端增加参数）
   + 能够显示最热文档推荐（需要切换成『最近最热』的文档）。
5. 数据库索引：
   - 方法一：对于这种，似乎索引中的第一个（grade）必须用，否则不会使用索引。
     - create index list_index ON docs (grade, genre, words);
   - 方法二：对于这种，似乎索引都能够用上，但是比较慢。
     - CREATE INDEX grade_index ON docs (grade);
     - CREATE INDEX genre_index ON docs (genre);
     - CREATE INDEX words_index ON docs (words);
     - CREATE INDEX doc_md_index ON docs (doc_md);
     - CREATE INDEX view_index on docs (view desc);
6. 用『.schema』可以看结构

## Table
Docs：

+ doc_id
+ creat_time
+ doc_slug
+ title、content
+ grade、genre、words
+ author、org
+ view、yesterday_view、today_view、update_time
+ former_url、former_org
+ tag：
+ same_titles？
+ ​