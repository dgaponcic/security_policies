import re

def my_f(text):
      exp = re.findall('(?<=<custom_item>)(.*?)(?=<\/custom_item>)',text,  re.S)
      all_lines = []
      for e in exp:
        obj = {}
        i = 0
        while i < len(e):
          tag = ''
          while i < len(e) and e[i] != ":":
            tag += e[i]
            i += 1
          
          i += 1

          res = ''
          if i < len(e):
            if e[i] == "'" or e[i] == '"':
              delimitator = e[i]
              i += 1
              while e[i] != delimitator:
                res += e[i]
                i += 1
            else:
              while i < len(e) and e[i] != "\n":
                res += e[i]
                i += 1

            obj[tag.strip()] = res.strip()
        all_lines.append(obj)
      return all_lines