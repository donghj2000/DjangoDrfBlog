# DjangoDrfBlog
基于django,restframework的博客后端，包括注册/登录，个人信息修改，文章列表，全文搜索等。
需要python 3.6 以上。

### vscode调试
```
在项目根目录下创建.vscode文件夹，将DjangoDrfBlog.code-workspace， launch.json， settings.json拷入其中， 即可调试。
```

### 创建虚拟环境
```
自行创建，也可以不创建。
```

### 安装依赖包
```
pip freeze > requirements.txt
```
### 执行数据库迁移
```
python manage.py mkmigrations
python manage.py migrate
```
### 注册新用户时通过邮箱激活，需要配置邮箱服务器。也可以修改代码，去掉激活功能。
```
EMAIL_HOST_PASSWORD 配置为邮箱第三方登陆的授权码，非自己的登陆密码。
```
### 全文搜索
```
支持 WhooshEngine 和 elasticsearch7。
elasticsearch7自带jdk，安装和运行过程中的一些错误：

es启动时需要使用非root用户，创建一个新用户：
useradd userxxx
为 userxxx 用户添加密码
passwd userxxx
将userxxx添加到sudoers
userxxx  ALL=(ALL:ALL)  NOPASSWD:ALL

运行过程中出现错误：
1，如果报jvm堆内存太小，修改jvm.options 的JVM heap size
-Xmx512m
2,
[1]: max file descriptors [4096] for elasticsearch process is too low, increase to at least [65536]
[2]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
用户最大可创建文件数太小
sudo vi /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
设置/etc/security/limits.conf
结果不生效，普通用户登陆后需要再次su - 用户名 才生效。
查看可打开文件数量
ulimit -Hn
3,
最大虚拟内存太小
sudo vi /etc/sysctl.conf 
vm.max_map_count=262144
查看虚拟内存的大小
sudo sysctl -p
```

### jwt登陆
```
djangorestframework-jwt==1.11.0
djangorestframework-simplejwt==4.4.0，
这2个库都可以，前一个功能更多点，但是只支持PyJWT 2.0以下版本，如果要支持2.0以上版本，需要自己做一些修改。
```

### 第三方登陆
```
采用social_django，前端界面有入口，后端没有调试过。
social_django需要PyJWT2.3，与 djangorestframework-jwt有冲突。通过修改djangorestframework-jwt使其适配PyJWT 2.3.
```
