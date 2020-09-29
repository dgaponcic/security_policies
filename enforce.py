import winreg
import os
import win32security

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

    def file_check(self, policy):
        file2check = policy["value_data"]
        condition = policy["file_option"]
        exists = os.path.isfile(file2check)
        if condition == "MUST_EXIST" and not exists:
            open(file2check)
            return {"status": 0, "msg": {"val": "MUST_NOT_EXIST", "content": None}}
        if condition == "MUST_NOT_EXIST" and exists:
            content = open(file2check).read()
            os.remove(file2check)
            return {"status": 0, "msg": {"val": "MUST_EXIST", "content": content}}
        return {"status": -1, "msg": f"Couldn't enforce"}

    def user_rights_policy(self, policy):
        actual_users = []
        granted = []
        deleted = []
        for val in win32security.LsaEnumerateAccountsWithUserRight(win32security.LsaOpenPolicy("", 25), policy["right_type"]):
            actual_users.append(win32security.LookupAccountSid(None, val)[0])
        file_users = policy["value_data"]
        if (file_users == '' or file_users == "Undefined") and len(actual_users) != 0:
            for user in actual_users:
                try:
                    win32security.LsaRemoveAccountRights(win32security.LsaOpenPolicy("", 25), win32security.LookupAccountName(None, user)[0], 0, [policy["right_type"]])
                    deleted.append(user)
                except Exception as e:
                    continue
            return {"status": 0, "msg": {"granted": granted, "deleted": deleted}}
        
        file_users = file_users.replace("'", "").replace('"', '').split('&&')
        file_users = [user.strip() for user in file_users]
        for user in file_users:
            try:
                if user not in actual_users:
                    win32security.LsaAddAccountRights(win32security.LsaOpenPolicy("", 25), win32security.LookupAccountName(None, user)[0], [policy["right_type"]])
                    granted.append(user)
            except Exception as e:
                continue
        for user in actual_users:
            try:
                if user not in file_users:
                    win32security.LsaRemoveAccountRights(win32security.LsaOpenPolicy("", 25), win32security.LookupAccountName(None, user)[0], 0, [policy["right_type"]])
                    deleted.append(user)
            except Exception as e:
                continue
        return {"status": 0, "msg": {"granted": granted, "deleted": deleted}}

    def enforce(self, policy):
        res = None
        policy_type = policy["type"]
        if policy_type == "REG_CHECK":
            res = self.reg_check(policy)
        elif policy_type == "FILE_CHECK":
            res = self.file_check(policy)
        elif policy_type == "USER_RIGHTS_POLICY":
            res = self.user_rights_policy(policy)
        else:
            res = {"status": -1, "msg": f"{policy_type} to be done"}
        return res
    