import time
def export(dayBefore = 0):
	return str(int(time.strftime("%d"))-dayBefore)+"/"+time.strftime("%m")+"/"+time.strftime("%Y")
def hourStr():
	return str(time.strftime("%H")+":"+time.strftime("%M"))