# Python modules
import matplotlib.pyplot as plt

# Own modules
import readFiles

def main():
	data=readFiles.readFiles()
	plt.plot(data.xkoord, data.ykoord, '.', alpha=0.05)
	plt.show()

print("execute main")
main()
print("done")