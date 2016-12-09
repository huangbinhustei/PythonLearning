i = 1790
while 1:
	print(i)
	i+=1
	if 0 == i%10:
		break
b = "i = " + str(i)

with open("/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/mycomposition/1/test.py" ,"r") as f:
	a = f.read()

with open("/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/mycomposition/1/test.py" ,"w") as f:
	f.write(a.replace("i = 1790",b))
