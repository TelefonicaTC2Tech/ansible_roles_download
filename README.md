# ansible_roles_download

This script contains a Python scrpt to download a roles form a file
with a Ansible Galaxy format.

The output of the file shown several things:

- If it is a New role download.
- A warning message if the branch of a previously downloaded role is different from the requeriments file
- A warning message if the branch of a previously downloaded role has unstagged/uncommited changes

# To-Do 

- Ability to specify other requeriments file different of `./requirements.txt`
- Add this repo a pypi installable with pip
