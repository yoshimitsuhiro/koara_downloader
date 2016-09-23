import os, sys, glob, time, requests, regex
from PIL import Image
from bs4 import BeautifulSoup

def main():
	automan = 1 #1 for auto, 2 for manual
	print("Please enter the URL of the book you wish to download:")
	while True:
		book_url = input('') #get URL of book
		if book_url[:29] == "http://project.lib.keio.ac.jp": break
		elif book_url[:29] == "http://koara-a.lib.keio.ac.jp": break
		else: print("Invalid input! Be sure to enter the full URL including http://.")
	print(u"Attempt to find author and title automatically (doesn't always work...) (y/n)?")
	while True:
		choice = input()
		if choice == "y" or choice == "Y" or choice == "yes" or choice == "YES":
			print("Searching for author and title...")
			filename = getinfo(book_url)
			break
		elif choice == "n" or choice == "N" or choice == "no" or choice == "NO":
			filename = "download"
			break
		else: print(u"Invalid input! Input yes or no.")
	getjpgs(book_url, filename, automan)
	print('All finished!')

def getinfo(book_url):
	gojuuonzu = [
		['a','i','u','e','o'],
		['ka','ki','ku','ke','ko'],
		['sa','si','su','se','so'],
		['ta','ti','tu','te','to'],
		['na','ni','nu','ne','no'],
		['ha','hi','hu','he','ho'],
		['ma','mi','mu','me','mo'],
		['ya','yi','yu','ye','yo'],
		['ra','ri','ru','re','ro'],
		['wa','wi','wu','we','wo']
	]
	book_id = book_url.split('/')[-2]
	id_elements = book_id.split('-')
	new_elements = id_elements
	for gyo in gojuuonzu:
		if id_elements[1] in gyo:
			kana_num = (gojuuonzu.index(gyo) * 5) + (gyo.index(id_elements[1]) + 1)
			if kana_num < 10:
				new_elements[1] = '0{0}'.format(kana_num)
			else: new_elements[1] = kana_num
	index = 1
	for i in id_elements[2:]:
		index += 1
		if int(i) < 10:
			new_elements[index] = '00{0}'.format(i)
		elif int(i) < 100:
			new_elements[index] = '0{0}'.format(i)
		else:
			new_elements[index] = i
	if len(id_elements) == 3:
		new_id = '50_{0}_{1}_{2}_000'.format(new_elements[0], new_elements[1], new_elements[2])
	elif len(id_elements) == 4:
		new_id = '50_{0}_{1}_{2}_{3}'.format(new_elements[0], new_elements[1], new_elements[2], new_elements[3])
	else: print('Error: Unrecognized format for book id!')
	new_url = 'http://koara-a.lib.keio.ac.jp/xoonips/modules/xoonips/detail.php?koara_id={0}'.format(new_id)
	soup = BeautifulSoup(requests.get(new_url).text)
	title = soup.find(text='タイトル').findNext('td').text.lstrip().rstrip()
	author = soup.find(text='著者').findNext('tr').text.lstrip().rstrip()
	if author == '': author = '作者未詳'
	code = soup.find(text='識別番号').findNext('tr').findNext('tr').text.lstrip().rstrip().split('：')[-1]
	filename = '{0} - {1} ({2})'.format(author, title, code)
	badchars = [r'\\', r'\/', r'\:', r'\*', r'\?', r'\"', r'\<', r'\>', r'\|']
	goodchars = ['＼', '／', '：', '＊', '？', '”', '＜', '＞', '｜']
	for i in badchars:
		if regex.search(regex.compile(i), filename): filename = regex.sub(regex.compile(i), goodchars[badchars.index(i)], filename)
	return(filename)

def getjpgs(book_url, filename, automan):
	#get URL for main directory of pages
	if book_url[-5:] == '.html': main_directory = book_url[:-5]
	elif book_url[-7:] == '#page=1': main_directory = book_url[:-7]
	else:
		print('URL format is unrecognized. URL must end in \"bookxxx.html\" or \"#page=1\".')
		sys.exit()
	num_pages = 1
	num_images = 1
	while True:
		if requests.head('{0}/page{1}/x4/1.jpg'.format(main_directory, num_pages)).status_code == 404:
			num_pages -= 1
			break
		else: num_pages += 1
	while True:
		if requests.head('{0}/page1/x4/{1}.jpg'.format(main_directory, num_images)).status_code == 404:
			num_images -= 1
			break
		else: num_images += 1
	print(book_url)
	print('Number of pages: {0}'.format(num_pages))
	firstpage = '{0}/page1/x4/'.format(main_directory)
	os.makedirs('cache', exist_ok=True)
	files = glob.glob('cache/*')
	for f in files:
		os.remove(f)
	print('Calculating page size...')
	scraper(firstpage, num_images)
	if automan == 1: ximages, yimages = autotester(book_url, num_images, filename)
	if automan == 2: ximages, yimages = manualtester(book_url, num_images, filename)
	for page in range(2, num_pages + 1):
		page_url = '{0}/page{1}/x4/'.format(main_directory, page)
		print('Downloading page {0}'.format(page))
		scraper(page_url, num_images) #download images
		im = merger(num_images, ximages, yimages)
		os.chdir(filename)
		im.save('page{0}.jpg'.format(page))
		os.chdir('..')
		files = glob.glob('cache/*')
		for f in files:
			os.remove(f)

def scraper(page_url, num_images):
	os.chdir('cache')
	for jpg in range(1, num_images + 1):
		r = requests.get('{0}{1}.jpg'.format(page_url, jpg))
		with open('{0}.jpg'.format(jpg), "wb") as f:
			f.write(r.content)
			f.closed
	os.chdir('..')

def manualtester(book_url, num_images, filename):
	print('{0} images per page.'.format(num_images))
	while True:
		while True:
			while True:
				try:
					ximages = float(input('How many images in the x axis? '))
					break
				except:
					print('Invalid input!')
			if ximages == 0 or ximages > num_images: print('Invalid input!')
			elif float(num_images/ximages).is_integer(): break
			else: print('Invalid input!')
		ximages = int(ximages)
		yimages = int(num_images/ximages)
		im = merger(num_images, ximages, yimages)
		im.show()
		while True:
			redo = input('Is this image the correct proportions? (y/n) ')
			if redo == 'Y' or redo == 'y' or redo == 'YES' or redo == 'yes': break
			elif redo == 'N' or redo == 'n' or redo == 'NO' or redo == 'no': break
			else: print('Invalid input!')
		if redo == 'Y' or redo == 'y' or redo == 'YES' or redo == 'yes': break
		else:
			while True:
				redo = input('Try again? (y/n)')
				if redo == 'Y' or redo == 'y' or redo == 'YES' or redo == 'yes': break
				elif redo == 'N' or redo == 'n' or redo == 'NO' or redo == 'no': break
				else: print('Invalid input!')
		if redo == 'N' or redo == 'n' or redo == 'NO' or redo == 'no':
			files = glob.glob('cache/*')
			for f in files:
				os.remove(f)
			os.rmdir('cache')
			sys.exit()
	os.makedirs(filename, exist_ok=False)
	os.chdir(filename)
	print('Downloading page 1')
	im.save('page1.jpg')
	os.chdir('..')
	return(ximages, yimages)

def autotester(book_url, num_images, filename):
	for ximages in range(1, num_images + 1):
		x = 0
		y = 0
		white = 0
		if float(num_images/ximages).is_integer():
			yimages = int(num_images/ximages)
			im = merger(num_images, ximages, yimages)
			x, y = im.size
			white = 0
			for i in range(0,y):
				r, g, b = im.getpixel((x-1,i))
				if r == 255 and g == 255 and b == 255:
					white += 1
		if white > 0 and white == y:
			print('{0} x {1} = Success!'.format(ximages, yimages))
			os.makedirs(filename, exist_ok=False)
			os.chdir(filename)
			print('Downloading page 1')
			im.save('page1.jpg')
			os.chdir('..')
			return(ximages, yimages)
		elif ximages == num_images:
			print('Error! No matches!')
			while True:
				redo = input('Try setting proportions manually? (y/n) ')
				if redo == 'Y' or redo == 'y' or redo == 'YES' or redo == 'yes': break
				elif redo == 'N' or redo == 'n' or redo == 'NO' or redo == 'no': break
				else: print('Invalid input!')
			if redo == 'Y' or redo == 'y' or redo == 'YES' or redo == 'yes': return(manualtester(book_url, num_images, filename))
			if redo == 'N' or redo == 'n' or redo == 'NO' or redo == 'no':
				files = glob.glob('cache/*')
				for f in files:
					os.remove(f)
				os.rmdir('cache')
				sys.exit()

def merger(num_images, ximages, yimages):
	os.chdir('cache')
	im = Image.open('1.jpg')
	x, y = im.size
	im = Image.open('{0}.jpg'.format(ximages))
	xlast = im.size[0]
	im = Image.open('{0}.jpg'.format(num_images))
	ylast = im.size[1]
	new_im = Image.new('RGB', (x*(ximages-1)+xlast, y*(yimages-1)+ylast))
	num = 1
	xaxis = []
	yaxis = []
	for i in range(0, ximages):
		xaxis.append(i*x)
	for i in range(0, yimages):
		yaxis.append(i*y)
	for i in yaxis:
		for j in xaxis:
			im = Image.open('{0}.jpg'.format(num)) 
			new_im.paste(im, (j,i))
			num += 1
	os.chdir('..')
	return(new_im)

if __name__ == "__main__":
	main()