nohup java -Xmx1024M -Xms1024M -jar <path/to/minecraft/server/jar> nogui >> <path/to/log.txt> 2>> <path/to/error.txt> & echo $! > <path/to/PID.txt>
