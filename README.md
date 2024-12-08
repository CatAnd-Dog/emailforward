
# 域名邮箱发信/收信/管理

教程-正在整理

部署：

简要

```
git clone https://github.com/CatAnd-Dog/emailforward.git

cd emailforward

cp .env.example .env

docker compose pull && docker compose up -d
```
初始管理员：

用户名：admin

密码：admin

## 用法
### 收信
假如你的域名为【user.458741.xyz】
那么所有发往 *@user.458741.xyz的邮件，你都可以在这儿查看到。比如  
a@user.458741.xyz   
b@@user.458741.xyzd   
等等所有的前缀，你都可以在这儿查到

![image](https://img.opaoai.com/i/2024/12/08/67555f3aa36ec.webp)

### 发信

同理，你可以使用任意的前缀去发送邮件   
假如你的域名为【ami.458741.xyz】  
那么你可以使用任意的前缀。比如   
a@ami.458741.xyz   
b@ami.458741.xyz
![image](https://img.opaoai.com/i/2024/12/08/67555e7746c49.webp)

图中的email-from就是你的前缀，图中的发信者即为a@ami.458741.xyz   


## 重要
修改env里面的密钥部分

强烈建议添加cf的5s盾


##  demo
[https://imail.opaoai.com](https://imail.opaoai.com)

![image](https://img.opaoai.com/i/2024/12/07/67542f06b3792.webp)

地址：[https://github.com/CatAnd-Dog/emailforward](https://github.com/CatAnd-Dog/emailforward)

教程：
[部署](https://oneperfect.cn/1335/)

[用户管理](https://oneperfect.cn/1351/)

[添加收信](https://oneperfect.cn/1337/)

[添加发信](https://oneperfect.cn/1369/)


## 更新日志
2024-12-8  
新增登录页公告，新增首页公共，新增版权信息，支持群发  
[修改方式](https://oneperfect.cn/1365/)


### 码字不易，点点start吧
