with open('test/ruby-billings') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

content.sort()
fp = open('ruby-data', 'w' )
for dt in content:
  fp.write(dt + '\n')