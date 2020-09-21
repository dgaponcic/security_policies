import re

def read_str(e, i):
  res = ''
  delimitator = e[i]
  i += 1
  while  i < len(e) and e[i] != delimitator:
    res += e[i]
    i += 1
  i += 1
  while  i < len(e) and e[i] == " ":
    i += 1
  while i < len(e) and (e[i] == "&" or e[i] == "|"):
    res += f"{e[i]}{e[i]}"
    i += 2
    if e[i] == ' ':
      i += 1
    delimitator = e[i]
    i += 1
    while i < len(e) and e[i] != delimitator:
      res += e[i]
      i += 1
    i += 1
    while i < len(e) and e[i] == " ":
      i += 1
  return res, i

def parse(text):
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
            while e[i] == " ":
              i += 1
            if e[i] == "'" or e[i] == '"':
              res, i = read_str(e, i)
            else:
              while i < len(e) and e[i] != "\n":
                res += e[i]
                i += 1
            key = tag.replace('\n', '')
            
            obj[key.strip()] = res.strip()
        all_lines.append(obj)
      return all_lines
