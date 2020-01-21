with open('test/python-billing') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

content.sort()
fp = open('python-data', 'w' )
for dt in content:
  fp.write(dt + '\n')