import subprocess

# из-за того, что исходные скрипты читают и отправляют сообщения бесконечно, а subprocess ждет завершения процесса,
# то сообщения отображаются некорректно?

client_write_proc = subprocess.Popen('python app/client_write.py', shell=False)
client_read_proc = subprocess.Popen('python app/client_read.py', shell=False)
client_read_proc.wait()
