#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging,os,sys, git

'''
This script requires the next python requirements:
- gitpython

Also a git command line installed in the servers

This script was tested with gitpython == 2.1.11 and git 2.24.2 using MacOS 10.15.04

'''

def prepareLoggin():
	# TO-DO prepare loggin from config file/ cmd line args
	FORMAT_FILE = '%(asctime)-15s %(levelname)s %(message)s'
	FORMAT_CONSOLE = '%(levelname)s %(message)s'

	rootLogger = logging.getLogger()

	# file handler
	# fileHandler = logging.FileHandler('requirements_download.log')
	# fileHandler.setFormatter(logging.Formatter(FORMAT_FILE))
	# rootLogger.addHandler(fileHandler)

	#console handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logging.Formatter(FORMAT_CONSOLE))
	rootLogger.addHandler(consoleHandler)

	rootLogger.setLevel(logging.INFO)


class DownloadRequirements():

	def __init__(self):
		'''Initializes class. '''
		self.working_directory = os.path.dirname(os.path.realpath(__file__))
		self.roles_directory = self.working_directory + "/roles"
		self.script_name = os.path.basename(__file__)
		logging.log(logging.DEBUG, self.working_directory)

		self.read_config_file_yml()

	def read_config_file_yml(self):
		import yaml
		fName = self.working_directory + "/requirements.yml"
		if os.path.exists(fName):
			with open(fName, 'r') as stream:
				try:
					self.role_requirements = yaml.load(stream, Loader=yaml.FullLoader)
				except yaml.YAMLError as exc:
					logging.log(logging.ERROR, exc)
					logging.log(logging.ERROR, "Aborting execution.")
					exit(1)
		else:
			logging.log(logging.ERROR, "No file exists: " + fName + " aborting execution.")
			logging.log(logging.ERROR, "A file named requirements.yml must exists along with " + self.script_name + ".")
			exit(1)

	def create_directory(self,directory):
		if not self.exists_directory(directory):
			try:
				os.makedirs(directory)
			except OSError as exc:
				logging.log(logging.ERROR, exc)
				return False
		
		return True

	def exists_directory(self,directory):
		if os.path.exists(directory):
			return True
		return False


	def run(self):
		'''iterate over configuration and download the repositories'''

		if not self.create_directory(self.roles_directory):
			logging.log(logging.ERROR, "Aborting execution. ")
			exit(1)

		for role in self.role_requirements:
			if (not "name" in role) or (not "src" in role):
				logging.log(logging.INFO, "role config line not understand: " + str(role) + " must provide 'name' and 'src' keys. Ignoring it.")
				continue

			method,git_url = role['src'].split('+')
			role_dir = self.roles_directory + "/" + role['name']

			if not "version" in role:
				logging.log(logging.DEBUG, "No version in requirements.yml for " + role['name'] + " using 'master' ")
				version="master"
			else:
				version=role['version']

			if not self.exists_directory(role_dir):

				logging.log(logging.INFO, "cloning: " +  git_url + " into: " + role_dir)
				try:
					git.Git(self.roles_directory).clone(git_url, role_dir)
					role_repo = git.Repo(role_dir)
					role_repo.git.checkout(version)
				except git.exc.GitError as exc: 
					logging.log(logging.ERROR, exc)
					logging.log(logging.ERROR, "Error cloning o doing checkout: " + role['name'])
					continue

			else:
				# Existing directory. Find out if it has a git repo and it is in the right branch
				try:
					role_repo = git.Repo(role_dir)
					branch_name = role_repo.git.rev_parse("--abbrev-ref","HEAD")
					status = role_repo.git.status("--porcelain")
				except git.exc.GitError as exc: 
					logging.log(logging.ERROR, exc)
					logging.log(logging.ERROR, "Not a valid Git repository? " + role['name'])
					continue
				
				if branch_name != version:
					logging.log(logging.WARNING, "Current branch: " + branch_name + " and version: " + version + " differs for role " + role['name'])

				if status != "":
					logging.log(logging.WARNING, "Current role: " + role['name'] + " has unstagged/uncommited changes")



if __name__ == "__main__":
	prepareLoggin()
	logging.log(logging.INFO, 'Starting download requirements...')
	download = DownloadRequirements()
	download.run()
	exit(0)