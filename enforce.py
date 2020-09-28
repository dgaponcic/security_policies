import winreg

class Enforcer:

  def reg_check(self, policy):
    try:
      item = policy["key_item"]
      path = policy["value_data"].replace("HKLM\\", "")
      hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
      val = policy["reg_option"]
      if item:
        result = winreg.QueryValueEx(hKey, item)
      if val == "MUST_NOT_EXIST":
        winreg.DeleteValue(hKey, item)
        return {"status": 0, "msg": "MUST_EXIST"}
      return {"status": -1, "msg": "Couldn't enforce"}
    except Exception as e:
      val = policy["reg_option"]
      if val == "MUST_EXIST":
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
        item = policy["key_item"]
        if item:
            winreg.SetValueEx(key, item, 0, winreg.REG_DWORD, 0)
        return {"status": 0, "msg": "MUST_NOT_EXIST"}
      return {"status": -1, "msg": "Couldn't enforce"}

  def enforce(self, policy):
    res = None
    policy_type = policy["type"]
    if policy_type == "REG_CHECK":
      res = self.reg_check(policy)

    else:
       res = {"status": -1, "msg": f"{policy_type} to be done"}
    return res
    