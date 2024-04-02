pid=$(ps -ax | grep "[p]ython exp" | awk '{print $1}')  
echo "exporter is running with pid: $pid"
kill -9 $pid
#customize home dir
cd ~
source ./bin/activate
nohup python exporter.py & 




