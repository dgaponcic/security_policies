import winreg
import random
import win32net
import win32service
import win32security
import os
from subprocess import check_output

class Executor:

  def reg_check(self, policy):
    try:
      item = policy["key_item"]
      path = policy["value_data"].replace("HKLM\\", "")
      hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
      val = policy["reg_option"]
      if item:
        result = winreg.QueryValueEx(hKey, item)
      if val == "MUST_EXIST":
        return {"status": 0, "msg": "Passed"}  
      return {"status": 1, "msg": f"File {path} must not exist"}
 
    except Exception as e:
      val = policy["reg_option"]
      if val == "MUST_NOT_EXIST":
        return {"status": 0, "msg": "Passed"}
      else:
        return {"status": 1, "msg": "File not found"}

  def password_policy_dword(self, check_data, actual_item, item):
    if ".." in check_data:
      vals = check_data.replace('[', "").replace(']', '').split("..")
      min_val, max_val = vals[0], vals[1]
      if min_val == "MIN":
        if actual_item < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 0, "msg": f"{item} should be less than {max_val}"}
      elif max_val == "MAX":
        if actual_item > int(min_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 0, "msg": f"{item} should be more than {min_val}"}
      else:
        if actual_item > int(min_val) and actual_item < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{item} should be more than {min_val} and less than {max_val}"}
    else:
      if int(check_data) == actual_item:
          return {"status": 0, "msg": "Passed"}
      else: 
        return {"status": 1, "msg": f"{item} should be {check_data}"}

  def password_policy(self, policy):
    res = win32net.NetUserModalsGet(None, 0)
    data = policy["value_data"]
    check_type = policy["password_policy"]
    if check_type == "ENFORCE_PASSWORD_HISTORY":
      return self.password_policy_dword(data, res["password_hist_len"], "Password history")
    elif check_type == "MAXIMUM_PASSWORD_AGE":
      return self.password_policy_dword(data, res["max_passwd_age"], "Maximum password age")
    elif check_type == "MINIMUM_PASSWORD_AGE":
      return self.password_policy_dword(data, res["min_passwd_age"], "Minimum password age")
    elif check_type == "MINIMUM_PASSWORD_LENGTH":
      return self.password_policy_dword(data, res["min_passwd_len"], "Minimum password length")
    elif check_type == "COMPLEXITY_REQUIREMENTS":
      return {"status": -1, "msg": "Password complexity requirements to be done"}
    elif check_type == "REVERSIBLE_ENCRYPTION":
      return {"status": -1, "msg": "Password reversible encryption to be done"}
    elif check_type == "FORCE_LOGOFF":
      if res["force_logoff"] and data == "Enabled":
        return {"status": 0, "msg": "Passed"}
      return {"status": 1, "msg": "Force logoff should be disabled"}
    return {"status": 1, "msg": f"{check_type} unknown check type"}


  def registry_setting_dword(self, check_data, actual_item, path, item):
    if ".." in check_data:
      vals = check_data.replace('[', "").replace(']', '').split("..")
      min_val, max_val = vals[0], vals[1]
      if min_val == "MIN":
        if actual_item < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 0, "msg": f"{item} at {path} should be less than {max_val}"}
      elif max_val == "MAX":
        if actual_item > int(min_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 0, "msg": f"{item} at {path} should be more than {min_val}"}
      else:
        if actual_item > int(min_val) and actual_item < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{item} at {path} should be more than {min_val} and less than {max_val}"}
    else:
      if int(check_data) == actual_item:
          return {"status": 0, "msg": "Passed"}
      else: 
        return {"status": 1, "msg": f"Item {item} at {path} should be {check_data}"}

  def registry_setting_multi_text(self, check_data, actual_item, item, path):
    check_data = check_data.replace("'", "").replace('"', '').split('&&')
    check_data = [data.strip() for data in check_data]
    for data in check_data:
      if data not in actual_item:
        return  {"status": 1, "msg": f"{data} not in {item} at {path}"}
    return  {"status": 0, "msg": "Passed"}

  def registry_setting(self, policy):
    item = policy["reg_item"]
    path = policy["reg_key"].replace("HKLM\\", "")
    try:
      hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
      option = policy["reg_option"]
      actual_item = winreg.QueryValueEx(hKey, item)[0]
      check_type = policy["value_type"]
      check_data = policy["value_data"]

      if check_type == "POLICY_SET":
        if check_data == "Enabled":
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{item} at {path} should be disabled"}
      elif check_type == "POLICY_MULTI_TEXT":
        return self.registry_setting_multi_text(check_data, actual_item, item, path)
      elif check_type == "POLICY_DWORD":
        return self.registry_setting_dword(check_data, actual_item, path, item)
      else:
        if check_data == actual_item:
          return {"status": 0, "msg": "Passed"}

      return {"status": 1, "msg": f"{item} at {path} shoul be {check_data}"}
    except:
      if "reg_option" in policy.keys() and policy["reg_option"] == "CAN_BE_NULL":
        return {"status": 0, "msg": "Passed"}
      return {"status": 1, "msg": f"No {item} at {path}"}

  def file_check(self, policy):
    file2check = policy["value_data"]
    condition = policy["file_option"]
    exists = os.path.isfile(file2check)
    if condition == "MUST_EXIST" and exists:
      return {"status": 0, "msg": "Passed"}
    if condition == "MUST_NOT_EXIST" and not exists:
      return {"status": 0, "msg": "Passed"}
    return {"status": 1, "msg": f"File {file2check} does not exist"}

  def lockout_policy(self, policy):
    res = win32net.NetUserModalsGet(None, 3)
    check_type = policy["lockout_policy"]
    data = policy["value_data"]
    is_range = False
    if '..' in data:
      is_range = True
    
    actual_val = None
    if check_type == "LOCKOUT_DURATION":
      actual_val = res["lockout_duration"]
    elif check_type == "LOCKOUT_THRESHOLD":
      actual_val = res["lockout_threshold"]
    else:
      actual_val = res["lockout_observation_window"]

    if is_range:
      vals = data.replace('[', "").replace(']', '').split("..")
      min_val, max_val = vals[0], vals[1]
      if min_val == "MIN":
        if actual_val < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{check_type} should be less than {max_val}"}
      elif max_val == "MAX":
        if actual_val > int(min_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{check_type} should be more than {min_val}"}
      else:
        if actual_val > int(min_val) and actual_val < int(max_val):
          return {"status": 0, "msg": "Passed"}
        else:
          return {"status": 1, "msg": f"{check_type} should be more than {min_val} and less than {max_val}"}
    else:
      if res["lockout_duration"] == data: 
        return {"status": 0, "msg": "Passed"}
      else:
        return {"status": 1, "msg": f"Incorrect data in {check_type}."}


  def user_rights_policy(self, policy):
    try:
        actual_users = []
        print(policy["right_type"])
        lsa_policy = win32security.LsaOpenPolicy("", 25)
        print(lsa_policy)
        users = win32security.LsaEnumerateAccountsWithUserRight(lsa_policy, policy["right_type"])
        for val in users:
            actual_users.append(win32security.LookupAccountSid(None, val)[0])
        file_users = policy["value_data"]
        if file_users == '':
            if len(actual_users) == 0:
                return {"status": 0, "msg": f"Passed"}
            else:
                return {"status": 1, "msg": f"There are users who are granted this permission"}
        file_users = file_users.replace("'", "").replace('"', '').split('&&')
        file_users = [user.strip() for user in file_users]
        
        for user in file_users:
            if user not in actual_users:
                return {"status": 1, "msg": f"User {user} not granted permission"}

        for user in actual_users:
            if user not in file_users:
                return {"status": 1, "msg": f"User {user} should not be granted permission"}
        return {"status": 0, "msg": f"Passed"}
    except Exception as e:
        print(e)
        return {"status": -1, "msg": f"To be done Acces Denied User Rights"}


  def audit_powershell(self, policy):
    try:
      res = check_output(f'powershell.exe "{policy["powershell_args"]}"', shell=True)
      if "only_show_cmd_output" in policy.keys():
        if policy["only_show_cmd_output"] == "YES":
          return {"status": 0, "msg": res}
      else:
        data = policy["value_data"]
        if data == res:
          return {"status": 0, "msg": "Passed"}
      return {"status": 0, "msg": f"Expected output was {res}"}
    except:
      return {"status": -1, "msg": f"Could not execute powershell with argument {policy['powershell_args']}"}


  def execute(self, policy):
    res = None
    policy_type = policy["type"]
    if policy_type == "REG_CHECK":
      res = self.reg_check(policy)
    elif policy_type == "REGISTRY_SETTING":
      res = self.registry_setting(policy)
    elif policy_type == "PASSWORD_POLICY":
      res = self.password_policy(policy)
    elif policy_type == "FILE_CHECK":
      res = self.file_check(policy)
    elif policy_type == "LOCKOUT_POLICY":
      res = self.lockout_policy(policy)
    elif policy_type == "USER_RIGHTS_POLICY":
      res = self.user_rights_policy(policy)
    elif policy_type == "AUDIT_POWERSHELL":
      res = self.audit_powershell(policy)
    else:
       res = {"status": -1, "msg": f"{policy_type} to be done"}
    return res
    