# DjangoDrfBlog
基于django,restframework的博客后端，包括注册/登录，个人信息修改，文章列表，全文搜索等。
需要python 3.6 以上。
发送邮件使用celery异步任务实现，如果要调试发送邮件，需要开启celery,进入到项目根目录
celery -A project worker --loglevel=info -P enventlet

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

# 部署

### 编译安装 nginx
```
服务器：ubuntu 18.04

编译安装 nginx
sudo apt-get install gcc
sudo apt-get install libpcre3 libpcre3-dev
sudo apt-get install zlib1g zlib1g-dev
sudo apt-get install openssl
sudo apt-get install libssl-dev

cd /usr/local
mkdir nginx
wget http://nginx.org/download/nginx-1.20.1.tar.gz
tar -xvf nginx-1.20.1.tar.gz

cd /usr/local/nginx-1.20.1
./configure --prefix=/usr/local/nginx --with-http_ssl_module
make
make install

配置文件  /usr/local/nginx/conf/nginx.conf
配置了3个前端端口 80,81,82分别对应vue,react,react_koa前端
配置了2个业务服务器端口 8000，3000，分别对应django,koa后端服务
如果要开启ssl，需要申请证书。测试环境下可以自己生成证书

查看防火墙是否关闭
sudo ufw status
关闭防火墙
sudo ufw disable
cd /usr/local/nginx/sbin
启动：
进入nginx的sbin目录，执行 ./nginx

项目目录:
/home/donghj/blog
后端：
/home/donghj/blog/backend
前端
/home/donghj/blog/frontend
vue:
/home/donghj/blog/frontend/dist_vue
react:
/home/donghj/blog/frontend/dist_react
koa:(需要配合koa后端)
/home/donghj/blog/frontend/dist_react_koa

```
### 安装uwsgi 和 python依赖包
```
pip install -r requirements.txt
pip3 install -r requirements.txt

安装 uwsgi
pip3 install uwsgi
sudo apt install uwsgi-core uwsgi-plugin-python3
启动 uwsgi --ini uwsgi.ini --plugin=python3
杀掉 uwsgi
ps aux | grep uwsgi
killall -s INT /usr/local/bin/uwsgi

开启celery,进入到项目根目录
celery -A project worker --loglevel=info -P enventlet
```

### docker 环境下的部署
```
安装 docker-ce，Docker Compose。

生成镜像
cd docker_k8s
docker build -t mypython:v1 .
运行镜像:
docker-compose up
访问：http://192.168.1.6:80, http://192.168.1.6:81  这里的IP是机器的物理IP.

注意docker-compose.yaml中的这两行
command: uwsgi --ini /code/backend/uwsgi_docker.ini
    uwsgi_docker.ini里的主机IP要写成这里本文件中的ipv4_address: 10.0.0.10
/usr/local/nginx/conf/nginx_docker.conf:/etc/nginx/nginx.conf
    nginx配置文件的后端服务IP也要改成这个IP
    
备注：镜像里没有加入celery启动的命令。
```
### k8s 环境下的部署
```
使用kubeadm安装k8s集群环境，版本1.23。此处安装了一个master(192.168.1.6) + 一个node(192.168.1.7)
将镜像导出，拷贝到node上，否则在node上找不到镜像。
docker save -o mypython_v1.tar mypython:v1
scp mypython_v1.tar 192.168.1.7:/home/donghj/
在node上导入：
docker load < mypython_v1.tar

在master上：
部署deployment
kubectl apply -f nginx-uwsgi-deploy.yaml
暴露服务：
kubectl apply -f nginx-uwsgi-svc.yaml

查看服务：
kubectl get svc:
nginx-uwsgi   NodePort    10.98.194.44   <none>        80:80/TCP,81:81/TCP   45s
说明服务已经成功的运行在80,81端口
访问：http://192.168.1.7:80,http://192.168.1.7:81
注意nginx-uwsgi-deployment.yaml中的　
path: /usr/local/nginx/conf/nginx_k8s.conf
nginx_k8s.conf配置文件的后端IP要写成localhost,uwsgi_k8s.ini文件里的IP也要写成localhost，
因为把uwsgi和nginx部署到一个pod里，在同个pod里的不同容器使用localhost通信.

以上都是基于sqlite数据库，mysql数据库的部署暂未考虑。
```
