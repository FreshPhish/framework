import csv

phishFile = open("data/PhishingSites.txt","w")
with open('verified_online_websites.csv', 'rb') as f:
    reader = csv.reader(f)
    rownum=0
    for row in reader:
	# Save header row.
	    if rownum == 0:
		header = row
	    else:
		colnum = 0
		for col in row:
  		    if header[colnum] == 'url':
		    	print '%-8s: %s' % (header[colnum], col)
			phishFile.write(col+"\n")
		    colnum += 1
		    
	    rownum += 1
	    if rownum >= 200:
		break;
phishFile.close()
