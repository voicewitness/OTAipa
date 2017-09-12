import os
import sys
import shutil
import zipfile
import biplist
import datetime
import re
import configparser 

reload(sys)
sys.setdefaultencoding('utf8') 


def analyse(packagePath, des, server, deployCA=None):
	analyseWithConfigData({
		'package':packagePath,
		'destination': des,
		'server': server,
		'CA': deployCA
		})

def analyseWithConfig(confPath):
	cf = configparser.ConfigParser()
	cf.read(confPath)
	package = cf.get("path", "package")
	destination = cf.get("path", "destination")
	server = cf.get("path", "server")
	deployCA = cf.get("path", "CA")
	analyseWithConfigData({'package':package,'destination':destination,'server':server,'deployCA':'deployCA'})

def analyseWithLocalConfig():
	curdir = os.path.dirname(os.path.realpath(__file__))
	analyseWithConfig(os.path.join(curdir,"config.ini"))

def rePath(dir,filepath):
	return os.path.join(dir,os.path.basename(filepath))

def resPath(path):
	if path is None:
		return None
	dir_path = os.path.dirname(path)
	if dir_path.strip()=='':
		curdir = os.path.dirname(os.path.realpath(__file__))
		return os.path.join(curdir, path)
	return path

def copyToDes(filepath, des):
	des_file = rePath(des,filepath)
	shutil.copy(filepath, des_file)
	return des_file

def analyseWithConfigData(config):
	ori_ipa = config.get('package')
	ori_CA = config.get('CA')
	server = config.get('server')
	des = config.get('destination')
	iconSize = config.get('iconsize')

	ori_ipa = resPath(ori_ipa)
	ori_CA = resPath(ori_CA)
	des_CA = None

	curdir = os.path.dirname(os.path.realpath(__file__))

	if not os.path.exists(des):
		print('>>>>creating destination')
		os.makedirs(des)
		print('    done.\n')
	
	print('>>>>move ipa')
	copyToDes(ori_ipa, des)
	des_ipa = rePath(server, ori_ipa)
	print('<<<<done.\n')
	if ori_CA is not None:
		copyToDes(ori_CA, des)
		des_CA = rePath(server, ori_CA)

	print('>>>>reading ipa')
	z_ipa = zipfile.ZipFile(ori_ipa, 'r')
	name_list = z_ipa.namelist()
	z_icon = find_icon_path(z_ipa)
	tmp_icon = os.path.join(curdir, z_icon)
	new_iconname = 'AppIcon.png'
	des_icon = os.path.join(des, new_iconname)
	t_icon = os.path.join(server, new_iconname)

	print('  >>extract icon')
	z_ipa.extract(find_icon_path(z_ipa),curdir)
	shutil.copy(tmp_icon, des_icon)
	shutil.rmtree(os.path.join(curdir,'Payload'))
	print('  >>reading info.plist')
	infoplist_data = z_ipa.read(find_plist_path(z_ipa))
	z_ipa.close()

	infoplist = biplist.readPlistFromString(infoplist_data)
	version = infoplist['CFBundleShortVersionString']
	build = infoplist['CFBundleVersion']
	version_display = version + build
	identifier = infoplist['CFBundleIdentifier']
	bundlename = infoplist['CFBundleDisplayName']
	print('<<<<done.\n')

	print('>>>>creating index.html')
	template_file = open(os.path.join(curdir, 'index_template.html'), 'r')

	template = template_file.read()
	# print(template)
	des_template = open(os.path.join(des,'index.html'),'w')
	if des_CA is not None:
		template = template.replace('{{SERVER_CA}}', des_CA)
		template = template.replace('{{SERVER_CA_EXIST}}', 'vi')
		template = template.replace('{{SERVER_CA_NOT_EXIST}}', 'hi')
	else:
		template = template.replace('{{SERVER_CA_EXIST}}', 'hi')
		template = template.replace('{{SERVER_CA_NOT_EXIST}}', 'vi')
	template = template.replace('{{BETA_NAME}}', bundlename)
	template = template.replace('{{BETA_VERSION}}', version_display)
	template = template.replace('{{BETA_ICON}}', new_iconname)
	template = template.replace('{{BETA_PLIST}}', os.path.join(server, 'manifest.plist'))
	template = template.replace(
	    '{{BETA_DATE}}', datetime.datetime.now().strftime('%Y-%m-%d-%h-%M-%s'))
	des_template.write(template)
	template_file.close()
	des_template.close()
	print('<<<<done.\n')
	print('>>>>creating manifest.plist')
	manifest = {'items': [
		{'assets': [
			{
				'kind': 'software-package',
				'url': des_ipa
			},
			{
				'kind': 'display-image',
				'url': t_icon
			},
			{
				'kind': 'full-size-image',
				'url': t_icon
			}],
		'metadata': {
			'bundle-identifier': identifier,
			'bundle-version': version_display,
			'kind': 'software',
			'title': bundlename
			}
		}]
	}
	biplist.writePlist(manifest, os.path.join(des,"manifest.plist"),False)
	print('<<<<done.\n')
	# return


def find_plist_path(zip_file):
	name_list = zip_file.namelist()
	pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
	for path in name_list:
		m = pattern.match(path)
		if m is not None:
			return m.group()
	print('Error:not found info.plist')

def find_icon_path(zip_file, size=''):
	if not zip_file:
		return

	name_list = zip_file.namelist()
	pattern = re.compile(r'Payload/[^/]*\.app/.*Icon'+size+'.*\.png')
	for path in name_list:
		m = pattern.match(path)
		if m is not None:
			return m.group()
	print('Error:not found icon in size',size)
	return


if __name__ == "__main__":
	analyseWithLocalConfig()