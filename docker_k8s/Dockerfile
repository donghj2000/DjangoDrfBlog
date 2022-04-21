FROM python:3.6.9             
LABEL author="Jerry"
RUN mkdir /code                     
ADD ./requirements.txt /code   
WORKDIR /code
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt \
&& rm -f requirements.txt      
EXPOSE 8000  
ADD run.sh /run.sh
RUN chmod 755 /run.sh                        
CMD ["/rum.sh"]
