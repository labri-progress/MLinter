# Dataset

Projects are extracted from public JavaScript projects from [GitHub](https://github.com)
and the linter used to make the analyses is [ESLint](https://eslint.org).

## Dependencies
- #### [Python](https://www.python.org)
The current version used for our experiments is 3.9.7  
You will also need to install those libraries:
- [pymongo](https://pypi.org/project/pymongo/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)

- #### [MongoDB](https://www.mongodb.com)
The current version used for our experiments is MongoDB 6.0.0 Community.
You will also need to copy the `.env.example` file to `.env` and fill the variables with your own values.

## Utilisation
Data extraction requires the following steps:
- [Working directories initialization](#working-directories-initialization)
- [GitHub projects list creation](#github-projects-list-creation)
- [Clone and configuration of the GitHub projects](#clone-and-configuration-of-the-github-projects)
- [ESLint's configuration and execution](#eslints-configuration-and-execution)
- [Database import](#database-import)
- [Dataset creation](#dataset-creation)

**⚠️ All commands below have to be executed from the root path of the ```/dataset``` folder.**

### Working directories initialization
First step is to create working directories.  
Simply run the following command:
```shell
sh 1_init_folders_structure.sh
```

One folder ```/output``` will be created, containing the following subfolders:
- ```/result```, containing the following subfolders:
  - ```/commit_id```: will contain files storing current commit id for each repository cloned
  - ```/repo_urls```: will contain files storing the repositories URLs to clone
- ```/tmp```: will contain all repositories cloned

**⚠️ If you execute this command, all previous data will be erased.**

### GitHub projects list creation
The next step is to create a list of GitHub projects.  
Simply run the following command:
```shell
sh 2_get_github_repo_list.sh
```

One file will be created in the folder ```/output/result/repo_urls```:
- ```dataset.txt```: will contain all the repositories URLs with more than 10k stars to clone

This file follows this format:
```
<repo_full_name>:<repo_clone_url>
```

### Clone and configuration of the GitHub projects
The next step is to clone the GitHub projects and clean them by removing useless files.  
The command is the following:
```shell
sh 3_clone_and_clean_repos.sh
```

All repositories from ```/output/result/repo_urls/dataset.txt``` are cloned in the folder ```/output/tmp```.  
Moreover, for each clone, the current commit id is stored in a file with the repo name in the folder
```/output/result/commit_id```.

### ESLint's configuration and execution
This step will launch the analysis of the repositories by specifying the configuration to use.  
Here is the command to execute:
```shell
sh 4_configure_and_execute_eslint.sh [-d] [-a]
```
- d *(optional)* - With this flag, the configuration file will activate only two rules. It is for development purpose.
- a *(optional)* - With this flag, the configuration file will activate all rules.
By default, the configuration file will activate all fixable and one liner rules.

ESLint is executed on all repositories with the chosen configuration.  
Analysis results for each repository are stored in the folder ```/output/result/linter``` as a JSON file with the
repository name.

### Database import
This next step aims to extract the data from the ESLint analysis to store it in database.  

**⚠️ From here, you need to have a MongoDB running and configured in `.env`.**

The command to execute is:
```shell
sh 5_export_errors_in_db.sh [-n <number_of_executions>] [-e <current_execution_number>]
```
- n *(default: 1)* - With this option, you could parallelize the execution of the extraction. It will split the rules
list in ```<number_of_executions>``` parts and execute the script on the ```<current_execution_number>``` part.
- e *(default: 0)* - Current execution number.

This command will parse and process the data extracted by ESLint.
At the end of the execution, one collection will be created for each rule in the database.
We also dump each rule collection in the folder ```/output/result/dump/linter-extraction```.

For debug purpose, we generate logs for each execution in the folder ```/output/logs```.

### Dataset creation
This last step aims to create the different datasets needed for the learning phase.  
Finally run the following command:
```shell
sh 6_extract_dataset_for_xp.sh [-n <number_of_executions>] [-e <current_execution_number>]
```
- n *(default: 1)* - With this option, you could parallelize the execution of the dataset creation. It will split the
rules list in ```<number_of_executions>``` parts and execute the script on the ```<current_execution_number>``` part.
- e *(default: 0)* - Current execution number.

For each rule a folder is created in the folder ```/output/result/dataset```.  
Each rule folder contains a sub-folder for each ratio.  
Each ratio folder contains a sub-folder for each size.  
Each size folder contains three sub-folders containing the 100 datasets for the:
- train
- balanced validation
- realistic validation

For debug purpose, we generate logs for each execution in the folder ```/output/logs```.
