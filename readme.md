# 很久的版本，需要更新

# 1. 转换方案

## 1.1. 从原始日志文件读取日志    

根据 user_id，逐条日志划分，之后将关键信息保存到 “ user_id.log” 的文件。
这一步结束后可以得到按照用户名字划分的所有日志。

## 1.2. 整合为 session

1. 根据 user 日志的 header 字段进行排序，同一个 header 的可以判断为一个 session
2. 同一个 session 按照时间排序，将第一条 http 通信的时间作为 session 的创建时间
3. session 之间按照 session 的创建时间进行排序

通过这三步，得到有序的 session 表。

## 1.3 判断爬虫

共实现了 4 种 规则：

1. 1s 内连续 session 的创建和访问超过 sessionThreshold 次 
2. 1s 内连续 http 会话通信超过 httpEventThreshold 次
3. 同一个 session 内，ip+request+response 都相同的 http 会话次数超过 repeatThreshold 次
4. http 通信的 header 为空的情况

# 附录
## 1. 日志组成

| Index | Label | Content |
| -- | -- | -- |
| 0 | 日期 | 2019-11-25 |
| 1 | 时间（毫秒） | 00:00:00,000 |
| 2  | 占位符 | - |
| 3  | 日志等级 | INFO |
| 4  | 模块 | cn.arp.icas.authorize2.log.LogAspect |
| 5  | 占位符 | - |
| 6  | ICAS-LOG | ICAS-LOG |
| 7  | 占位符 | \| |
| 8  | 线程号 | 131 |
| 9  | 机构代码 | 112111 |
| 10  | user_id | 112111-17410 |
| 11  | 使用的api | /fin/arBillAssmbly/getBgBalanceDetail |
| 12 | HTTP方法 | GET |
| 13 | HTTP状态码 | 200 |
| 14 | 未知 | ["java.lang.String","java.lang.String","java.lang.String","java.lang.String","java.lang.String","java.lang.String"]  |
| 15 | parameter | ["coCode","parentId","tabName","offset","limit","searchKeyWord"] |
| 16 | parameter_value |["112111","task_11652SUM","v_bg_balance_detail","1","10",""]|
| 17 | header | [{"httpOnly":false,"maxAge":-1,"name":"__guid","secure":false,"value":"113044420.4477104904044561000.1573702078455.0176","version":0},{"httpOnly":false,"maxAge":-1,"name":"Authorization","secure":false,"value":"dXlTAbmVlwZZ","version":0}] |
| 18 | Name | 张三 |
| 19 | IP | 159.25.35.65 |
| 20 | Port | 215|


## 2. 常见的多次重复出现的日志URL

| Index | URL | Method | 
| -- | -- | -- | 
1 | /fa/purchase/assetOrder/remoteGetPagedAssetOrderListByModel | GET
2 | /fin/arBillAssembly/getRefInfoList | POST  
3 | /hr/thrpeople | POST 
4 | /fa/purchase/assetOrder/remoteGetPagedAssetOrderListByModel | POST