import random

class Executor:

  def reg_check(self, policy):
    a = random.random()
    policy_type = policy["body"][0]["value"]
    if a > 0.5:
      return {"status": 0, "msg": policy_type}
    else:
      return {"status": 1, "msg": policy_type}


  def password_policy(self, policy):
    a = random.random()
    policy_type = policy["body"][0]["value"]
    if a > 0.5:
      return {"status": 0, "msg": policy_type}
    else:
      return {"status": 1, "msg": policy_type}


  def execute(self, policy):
    res = None
    policy_type = policy["body"][0]["value"]
    if policy_type == "PASSWORD_POLICY":
      res = self.password_policy(policy)
    elif policy_type == "REG_CHECK":
      res = self.reg_check(policy)
    # elif policy_type == "FILE_CHECK":
    #   print("policy")
    # elif policy_type == "REGISTRY_SETTING":
    #   print("policy")
    # elif policy_type == "WMI_POLICY":
    #   print("policy")
    # elif policy_type == "AUDIT_POWERSHELL":
    #   print("policy")
    # elif policy_type == "SERVICE_POLICY":
    #   print("policy")
    # elif policy_type == "AUDIT_POLICY":
    #   print("policy")
    # elif policy_type == "USER_RIGHTS_POLICY":
    #   print("policy")
    # elif policy_type == "LOCKOUT_POLICY":
    #   print("policy")

    return res