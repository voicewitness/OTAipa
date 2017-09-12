# coding=UTF-8
import os
import paramiko

def ipaPath(testType,version,isAplipaySimulator=False):
	testtype_path_dict = {
		'release': 'release',
		'test': 'test',
	}
	testtype_path = testtype_path_dict.get(testType)
	path = os.path.join('IOS',testtype_path,version)
	return path

def sftp_download(host,port,username,password,local,remote):
	print('remote'+remote)
	sf = paramiko.Transport((host,port))
	sf.connect(username = username,password = password)
	sftp = paramiko.SFTPClient.from_transport(sf)
	try:
		# if os.path.isdir(local):#判断本地参数是目录还是文件
		for f in sftp.listdir(remote):#遍历远程目录
			print(f)
				# sftp.get(os.path.join(remote+f),os.path.join(local+f))#下载目录中文件
		# else:
			# sftp.get(remote,local)#下载文件
	except Exception,e:
		print('download exception:',e)
	sf.close()

if __name__ == "__main__":
	sftp_download(Server, port, User, Psw, '', ipaPath('test','1.0.0'))