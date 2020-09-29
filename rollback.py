import winreg
import win32security

class Rollbacker:

  def reg_check(self, policy, val):
    try:
        item = policy["key_item"]
        path = policy["value_data"].replace("HKLM\\", "")
        hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
        if item:
            result = winreg.QueryValueEx(hKey, item)
        if val == "MUST_NOT_EXIST":
            winreg.DeleteValue(hKey, item)
            return {"status": 0, "msg": "Success"}
        return {"status": -1, "msg": "Couldn't rollback"}
    except Exception as e:
        if val == "MUST_EXIST":
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
            item = policy["key_item"]
            if item:
                winreg.SetValueEx(key, item, 0, winreg.REG_DWORD, 0)
            return {"status": 0, "msg": "Success"}
        return {"status": -1, "msg": "Couldn't rollback"}

  def file_check(self, policy, condition):
    file2check = policy["value_data"]
    condition = condition["val"]
    exists = os.path.isfile(file2check)
    if condition == "MUST_EXIST" and not exists:
        open(file2check)
        return {"status": 0, "msg": "Success"}
    if condition == "MUST_NOT_EXIST" and exists:
        os.remove(file2check)
        return {"status": 0, "msg": "Success"}
    return {"status": -1, "msg": f"Couldn't enforce"}

  def user_rights_policy(self, policy, val):
    granted = val["granted"]
    deleted = val["deleted"]
    for user in granted:
        try:
            win32security.LsaRemoveAccountRights(win32security.LsaOpenPolicy("", 25), win32security.LookupAccountName(None, user)[0], 0, [policy["right_type"]])
        except Exception as e:
            continue
    for user in deleted:
        try: 
            win32security.LsaAddAccountRights(win32security.LsaOpenPolicy("", 25), win32security.LookupAccountName(None, user)[0], [policy["right_type"]])
        except Exception as e:
            continue
    return {"status": 0, "msg": "Success"}

  def rollback(self, policy, val):
    res = None
    policy_type = policy["type"]
    if policy_type == "REG_CHECK":
        res = self.reg_check(policy, val)
    elif policy_type == "FILE_CHECK":
        res = self.file_check(policy, val)
    elif policy_type == "USER_RIGHTS_POLICY":
      res = self.user_rights_policy(policy, val)
    else:
        res = {"status": -1, "msg": f"{policy_type} to be done"}
    return res
    