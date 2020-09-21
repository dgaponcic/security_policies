# security_policies

A tool for parsing and running audit security policies.

The application is written in Python, for GUI used PyQT.

The files are written in a XML-like language.

Parsed policy is stored under a name in Mongo database.

### To run the program:
* make sure you have mongo db running on localhost, port 27017
* make sure all files are in current directory
* execute "python app.py" 

### Execute
Execution is work in progress.

For now the following types of custom_item are executed:
* REG_CHECK
* REGISTRY_SETTING
* PASSWORD_POLICY
* FILE_CHECK
* LOCKOUT_POLICY
* USER_RIGHTS_POLICY
* AUDIT_POWERSHELL


### Demo 
Here you can see how to import a policy and review the policy before submitting. Once submitted you are asked to introduce a name for the policy. After submision the policy is parsed and stored in a mongo database. We can also perform search on policies and choose what rules we want to add, then save to a new document or update an existing one.

<img src="https://github.com/dgaponcic/security_policy_parser/blob/master/lab2.gif">

After execution, in the output we can see:
* Green policies - The policies passed.
* Red policies - An error occured, you can find the error in the output.
* Blue policies - Work in progress. To be done.

TODO add demo execution
