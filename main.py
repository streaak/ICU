#!/usr/bin/python

import os, sys, MySQLdb, time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

connection = MySQLdb.connect (host = "localhost", user = "rjp", passwd = "1484", db = "recon")
cursor = connection.cursor()


def list_subdomains():
	sub_domain = raw_input('[Domain] > ')
	cursor.execute ("select Domain, Active from domains where TopDomainID = (select DomainID from domains where Domain = %s) order by Domain", (sub_domain,))
	data = cursor.fetchall()

	for row in data:
		if ord(row[1]):
			print bcolors.OKGREEN + row[0] + bcolors.ENDC
		else:
			print bcolors.WARNING + row[0] + bcolors.ENDC	

	raw_input("\nPress any key to go back...")
	start()


def run_subdomain_scan_on_target(top_domain_par = None):
	if top_domain_par is None:
		print "What is the domain?"
		top_domain = raw_input('[Domain] > ')
	else:
		top_domain = top_domain_par

	os.system("python " + os.path.dirname(os.path.abspath(__file__)) + "/database/additional_tools/sublister_to_db.py " + top_domain + " NULL")

def insert_topdomain(top_domain_par = None):
	if top_domain_par is None:
		print "What is the domain? "
		top_domain = raw_input('[Domain] > ')
	else:
		top_domain = top_domain_par

	cursor.execute ("select * from domains where Domain = %s", (top_domain,))
	data = cursor.fetchone()  

	if data:
    		print bcolors.WARNING + "Domains already exists; program: " + str(data[1]) + ", last modified: " + str(data[6]) + bcolors.ENDC
		raw_input("Press any key to go back...")
		start()
	

	print "What is the program? "
	program = raw_input('[program] > ')

	print "Inscope? "
	inscope = raw_input('[Inscope] > ')
	if "no" not in inscope.lower():
		inscope = 1
	else:
		inscope = 0
	

	cursor.execute("INSERT INTO domains (Program, InScope, Domain, Active) VALUES (%s, %s, %s, %s)", (program, inscope, top_domain, 1))
	connection.commit()
	
	print bcolors.OKGREEN + "Domain added" + bcolors.ENDC
	raw_input("\nPress any key to go back...")
	start()


def insert_subdomain(top_domain_par = None):
	if top_domain_par is None:
		print "What is the (top)domain? "
		top_domain = raw_input('[(Top)Domain] > ')
	else:
		top_domain = top_domain_par

	cursor.execute ("select * from domains where Domain = %s", (top_domain,))
	data = cursor.fetchone()  

	if not data:
    		print bcolors.WARNING + "Domain not found!" + bcolors.ENDC
		print "Do you want to add it? "
		answer = raw_input('[yes/no] > ')
		if "no" not in answer.lower():
			insert_topdomain(top_domain)
		else:
			raw_input("Press any key to go back...")
			start()

	program = str(data[1])
	topdomainid = int(data[0])



	print "What is the subdomain? "
	sub_domain = raw_input('[(Subdomain] > ')

	cursor.execute ("select * from domains where Domain = %s", (sub_domain,))
	data = cursor.fetchone()  

	if data:
    		print bcolors.WARNING + "Subdomains already exists; program: " + str(data[1]) + ", last modified: " + str(data[6]) + bcolors.ENDC
		does_not_exist = False
	else:
		does_not_exist = True

	if does_not_exist:
		print "Inscope? "
		inscope = raw_input('[Inscope] > ')
		if "no" not in inscope.lower():
			inscope = 1
		else:
			inscope = 0

		cursor.execute("INSERT INTO domains (Program, InScope, Domain, Active, TopDomainID) VALUES (%s, %s, %s, %s, %s)", (program, inscope, sub_domain, 1, topdomainid))
		connection.commit()
		
		print bcolors.OKGREEN + "Domain added" + bcolors.ENDC

	print "Do you want to add another one?? "
	another_one = raw_input('[yes/no] > ')
	if "no" not in another_one.lower():

		insert_subdomain(top_domain)

	raw_input("\nPress any key to go back...")
	start()



def list_domains():
	cursor.execute ("select Domain, Active from domains where TopDomainID is NULL")
	data = cursor.fetchall()

	for row in data:
		if ord(row[1]):
			print bcolors.OKGREEN + row[0] + bcolors.ENDC
		else:
			print bcolors.WARNING + row[0] + bcolors.ENDC	
	
	raw_input("\nPress any key to go back...")
	start()


options = {1 : insert_topdomain,
           2 : list_subdomains,
           3 : list_domains,
           4 : insert_subdomain,
	   5 : run_subdomain_scan_on_target
}


def start():
	os.system('clear')
	cursor.execute ("select count(*) from domains where TopDomainID is NULL;")
	data = cursor.fetchall()
	sub_domains = data[0][0]

	cursor.execute ("select count(TopDomainID) from domains")
	data = cursor.fetchall()
	top_domains = data[0][0]

	domains = top_domains + sub_domains

	banner = """ {0}---------------+-------
 Domains       | {1}   
 Top-domains   | {2}  
 Sudomains     | {3}   
---------------+-------{4}"""

	choices = """
1. Add domain
2. List subdomains from domain
3. List all (top)domains
4. Add subdomain
5. Run subdomain scan on top domain
"""

	print banner.format(bcolors.HEADER, domains, sub_domains, top_domains, bcolors.ENDC)

	print choices.format()

	try:
		num = raw_input('> ')
		num = int(num)
	except:
		print "Provide a number please,"
		raw_input("\nPress any key to go back...")
		start()
		start()

	options[num]()


start()
cursor.close ()
connection.close ()
sys.exit()
