# MLinter
The project aims to extract data from linters in order to train learning models.  
Currently the projects are extracted from public JavaScript projects from [GitHub](https://github.com)
and the linter used to make the analyses is [ESLint](https://eslint.org).

## Dependencies
- #### [Node.js](https://nodejs.org)
The current version used for our experiments is 14.16.1

- #### [Python](https://www.python.org)
The current version used for our experiments is 3.9.7  
You will also need to install those libraries:
- [pymongo](https://pypi.org/project/pymongo/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)

## Utilisation
Data extraction requires the following steps:
- [Working directories initialization](#working-directories-initialization)
- [GitHub projects list creation](#github-projects-list-creation)
- [Clone and configuration of the GitHub projects](#clone-and-configuration-of-the-github-projects)
- [ESLint's configuration and execution](#eslints-configuration-and-execution)
- [Data extraction](#data-extraction)
- [Ground truth creation](#ground-truth-creation)

**⚠️ All commands below have to be executed from the root path of the repository.**

### Working directories initialization
First step is to create working directories.  
Simply run the following command:
```shell
sh 1_init_folders_structure.sh
```

One folder ```/output``` will be created at the root of the repository, containing the following subfolders:
- ```/result```, containing the following subfolders:
  - ```/repo_urls```: will contain files storing the repositories URLs to clone
  - ```/commit_id```, containing the following subfolders:
    - ```/dataset```: will contain files storing current commit id for repositories cloned for dataset creation
    - ```/ground_truth```: will contain files storing current commit id for repositories cloned for ground truth creation
  - ```/data```, containing the following subfolders:
    - ```/dataset```: will contain the dataset data
    - ```/ground_truth```: will contain the ground truth data
- ```/tmp```, containing the following subfolders:
  - ```/dataset```: will contain all repositories cloned for the dataset creation
  - ```/ground_truth```: will contain all repositories cloned for the ground truth creation

**⚠️ If you execute this command, all previous data will be erased.**

### GitHub projects list creation
The next step is to create a list of GitHub projects.  
Simply run the following command:
```shell
sh 2_get_github_repo_list.sh [-n <entier>]
```
- n *(optional)* - number of projects to get for dataset. *(default: 10)*

Two files will be created in the folder ```/output/result/repo_urls```:
- ```dataset.txt```: will contain ***n*** repositories URLs to clone for dataset creation
- ```ground_truth.txt```: will contain ***n*** repositories URLs to clone for ground truth creation

Those files follow this format:
```
<repo_name>:<repo_clone_url>
```

### Clone and configuration of the GitHub projects
The next step is to clone the GitHub projects and configure each required dependencies to execute ESLint.  
The command is the following:
```shell
sh 3_clone_and_clean_repos.sh
```

The following steps will be executed for both **dataset** and **ground truth**.  
All repositories from ```/output/result/repo_urls/[dataset|ground_truth].txt``` are cloned in the folder
```/output/tmp/[dataset|ground_truth]```.  
For each repository, we put a new ***package.json*** file and dependencies are installed.  
Moreover, for each clone, the current commit id is stored in a file with the repo name in the folder
```/output/result/commit_id/[dataset|ground_truth]```.

### ESLint's configuration and execution
This step will launch the analysis of the repositories by specifying the configuration to use.  
Here is the command to execute:
```shell
sh 4_configure_and_execute_eslint.sh [-a]
```
- a *(optional)* - If this option is passed, the configuration file will activate all rules, otherwise it
will only activate the fixable rules.

The following steps will be executed for both **dataset** and **ground truth**.  
ESLint is executed on all repositories with the chosen configuration.  
Analysis results for each repository are stored in the folder ```/output/result/linter/[dataset|ground_truth]``` as a
JSON file with the repository name.

### Data extraction
This next step aims to extract the data from the ESLint analysis to create dataset.  
Here is the command to execute:
```shell
sh 5_export_errors_in_db.sh
```

This command will parse and process the data extracted by ESLint. At the end of the execution, it will generate
a folder named ```/dataset``` in path ```/output/result/data```:

In this folder, there will have for each rule identified:
- one file ***<rule_name>.csv*** containing data extracted for the rule with this format:
```csv
repo,path,commitId,content,ruleId,hasError,isRandom
```
- one file ***<rule_name>_statistics.json*** with some statistics on the data extracted.

### Ground truth creation
This last step aims to create the ground truth in order to validate the models.  
Finally run the following command:
```shell
sh 6_extract_dataset_for_xp.sh
```

This last command will create a folder named ```/ground-truth``` in path ```/output/result/data``` and will contain for
each rule identified one file ***<rule_name>.json*** with the following format:
```json
[
  {
    "path": "path/to/file",
    "content": "content of the file",
    "errors": [
      {
        "beginLine": "begin line of the error",
        "endLine": "end line of the error"
      }
    ]
  }
]
```

**The last two tasks are independent and can therefore be executed in parallel.**
