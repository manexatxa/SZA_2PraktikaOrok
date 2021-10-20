#!/usr/bin/env python3
# Egileak - T4 Pablo Ruiz eta Laura Marquinez 

import socket, sys, select

zenbakiak = [0,1,2,3,4]
testuak = ["Irten","Eguzki-plakak","Bateria kargak","Propultzailea","Sentsore datuak"]
mez_tam = 1024
Xkodea = 11111


#menua
def menua():
	print("");
	print("ZundaAPP 2018 (c)")
	print("Sakatu egin nahi dezun ekintzaren zenbakia:")
	for i in range(0, len(zenbakiak)):
		print("  --  "+str(zenbakiak[i]) + " -- " + testuak[i]+".")

#Errore-mezuak inprimatzeko metodoa.
def erroreakTratatu(e):
	if( e == 1 ):
		print("Komando ezezaguna.")
	elif( e == 2 ):
		print("Espero ez zen parametroa. Parametro bat jaso da espero ez zen tokian.")
	elif( e == 3 ):
		print("Hautazkoa ez den parametro bat falta da.")
	elif( e == 4 ):
		print("Parametroak ez du formatu egokia.")
	elif( e == 5 ):
		print("Segurtasun kode okerra.")
	elif( e == 11 ):
		print("Eguzki plakak zabaltzea ezinezkloa da.")
	elif( e == 12 ):
		print("Ekintza hau aurretik eginda dago.")
	elif( e == 21 ):
		print("Ezinezkoa da bateriaren karga eskuratzea.")
	elif( e == 31 ):
		print("Propultsioarekin hastea ezinezkoa da.")
	elif( e == 32 ):
		print("Ezin zaio eutsi adierazitako iraupenari.")
	elif( e == 41 ):
		print("Sentsoreen neurketak ezin dira eskuratu.")
	else:
		print("Protokolo errore bat egon da.")
	print("Saiatu berriro.")

#Eguzki-plakak zabaltzeko eta tolesteko metodoa.
def eguzkiPlakak(s):
	parametroEgokiak = False;
	# Eguzki-plakak zabaldu edo tolestu piztu nahi den galdetzen da.
	while parametroEgokiak == False :
		print("Eguzki-plakak ireki zabaldu edo tolestu nahi dituzu?");
		print("Zabaldu. Sartu 0 zenbakia");
		print("Tolestu. Sartu 1 zenbakia");
        #Aukeratutako zenbakia
		parametroak = input();
		if parametroak == "0" or parametroak == "1" :
			parametroEgokiak = True;
		else:
			print("Zenbaki desegokia, saiatu berriro.");
	#Segurtasun-kodearen konprobaketa
	segurtasun_kodea = "";
	if parametroak == "0" or parametroak == "1":
		kodeOkerra = True;
		while kodeOkerra:
			try:
                #Segurtasun-kodea sartu
				segurtasun_kodea = int (input("Sartu segurtasun-kodea (5 digitu): "));
                #Segurtasun-kodea konprobatu
				if(segurtasun_kodea == Xkodea): 					
						kodeOkerra = False;					
				else:
					print("Segurtasun-kodea okerra. Saiatu berriro:");
			except ValueError:
				print("Segurtasun-kodea okerra. Saiatu berriro:");
        #FOLD komandoa + segurtasun kodea + zabaldu(0) edo tolestu(1)
		komandoa = "FOLD" + str(segurtasun_kodea) + str(parametroak);
        #Bidali guztia
		s.sendall(komandoa.encode('ascii'));
        #Jaso erantzuna
		erantzuna = s.recv( mez_tam ).decode('ascii');
		# Erantzuna aztertzen da ("OK" erantzun egokia eta "ER" erantzun okerra beraz, errore kudeaketa)
		if erantzuna[0:2] == "OK":
				if parametroak == "0":
					print("Eguzki-plakak zabaltzea lortu da.");
				else:
					print("Eguzki-plakak tolestea lortu da.")
		elif erantzuna[0:2] == "ER":
			errore = str(erantzuna[2:])
			# Errore-metodoari deitu dagokion errore-kodearekin.
			try:
				erroreakTratatu(int(errore));
			except ValueError:
				print("Protokolo errore bat egon da1.");
		else:
			print("Protokolo errore bat egon da2.");	


# Baterien karga jasotzeko metodoa.
def bateriaKargak(s):
	segurtasun_kodea = "";
	#Segurtasun-kodearen konprobaketa
	kodeOkerra = True;
	while kodeOkerra:
		try:
            #Segurtasun-kodea sartu
			segurtasun_kodea = int (input("Sartu segurtasun_kodea (5 digitu): "));
            #Segurtasun-kodea konprobatu
			if segurtasun_kodea == Xkodea: 					
					kodeOkerra = False;
			else:
				print("Segurtasun-kodea okerra. Saiatu berriro:");
		except ValueError:
			print("segurtasun-kodea okerra. Saiatu berriro:");
    #BATT komandoa + segurtasun kodea
	komandoa = "BATT" + str(segurtasun_kodea);
    #Guztia bidali
	s.sendall(komandoa.encode('ascii'));
    #Erantzuna jaso
	erantzuna = s.recv( mez_tam ).decode('ascii');
	# Erantzuna aztertzen da ("OK" erantzun egokia eta "ER" erantzun okerra beraz, errore kudeaketa)
	if erantzuna[0:2] == "OK":
        #Erantzuna gorde, OK gabe
		erantzuna = erantzuna[2:];
        #Erantzuna banatu split-ren bidez
		ehunekoa = erantzuna.split(":");
		print("Baterien karga honako hau da:");
        #Bateriaren karga pantailaratzeko moduan jartzeko
		for i in range(0, len(ehunekoa)):
			ehunekoa = ehunekoa[i]
			print("%"+ ehunekoa[0] + ehunekoa[1] + "," + ehunekoa[2]);
	elif erantzuna[0:2] == "ER":
		errore = erantzuna[2:]
		# Errore-metodoari deitu dagokion errore-kodearekin.
		try:
			erroreakTratatu(int(errore));
		except ValueError:
			print("Protokolo errore bat egon da1.");
	else:
		print("Protokolo errore bat egon da2.");


#Propultsaile bat denbora-tarte mugatu batean martxan jartzeko metodoa
def propultzailea(s):
	#Lehenik propultsailea hautatu (Digitu bat)
	propultsaileaHautatua = "";
	propultsaileEgokia = False;
	while (propultsaileEgokia == False):
		print ("Nahi duzun propultzailearen zenbakia sartu(Digitu bat):");
		try:
            #Sartu propultsailearen zenbakia(0-9)
			propultsaileaHautatua = int(input());
			if (propultsaileaHautatua>=0 and propultsaileaHautatua<10):
				propultsaileEgokia = True;
			else:
				print("Zenbaki okerra. Saiatu zaitez berriro.");	
		except ValueError:
			print("Zenbaki dezimal desegokia. Saiatu zaitez berriro.");
	#Bigarrenik denbora ezarri (3 digitu)
	denbora = "";
	denboraEgokia = False;
	while (denboraEgokia == False):
		print ("Nahi duzun denbora sartu milisegundotan(3 digitu):");
		try:
            #Sartu iraupena non propultsatzaile bakoitzaren iraupen maximoa: zenbakia * 100. 0 zenbakiarena ezik 550-ekoa dela.
			denbora = int(input());
			if denbora>0 and denbora<1000:
				denboraEgokia = True;
			else:
				print("Zenbaki okerra. Saiatu zaitez berriro.");	
		except ValueError:
			print("Zenbaki dezimal desegokia. Saiatu zaitez berriro.");
	segurtasun_kodea = "";
	#Segurtasun-kodearen konprobaketa
	kodeOkerra = True;
	while kodeOkerra:
		try:
            #Segurtasun-kodea sartu
			segurtasun_kodea = int (input("Sartu segurtasun_kodea(5 digitu): "));
            #Segurtasun-kodea konprobatu
			if(segurtasun_kodea == Xkodea): 					
					kodeOkerra = False;
			else:
				print("Segurtasun-kodea okerra. Saiatu berriro:");
		except ValueError:
			print("segurtasun-kodea okerra. Saiatu berriro:");
    #PROP komandoa + segurtasun kodea + propultsailearen zenbakia + iraupena
	komandoa = "PROP" + str(segurtasun_kodea) + str(propultsaileaHautatua) + str(denbora);
    #Guztia bidali
	s.sendall(komandoa.encode('ascii'));
    #Erantzuna jaso
	erantzuna = s.recv( mez_tam ).decode('ascii');
	# Erantzuna aztertzen da ("OK" erantzun egokia eta "ER" erantzun okerra beraz, errore kudeaketa)
	if erantzuna[0:2] == "OK":
		print("Ekintza burututa. Propultsailea denbora-tarte mugatu batean martxan egongo da.");
	elif erantzuna[0:2] == "ER":
		errore = erantzuna[2:]
		# Errore-metodoari deitu dagokion errore-kodearekin.
		try:
			erroreakTratatu(int(errore));
		except ValueError:
			print("Protokolo errore bat egon da1.");
	else:
		print("Protokolo errore bat egon da2.");

#Sentsoreen neurketen datuak jasotzeko metodoa.
def sentsoreDatuak(s):
	segurtasun_kodea = "";
	#Segurtasun-kodearen konprobaketa
	kodeOkerra = True;
	while kodeOkerra:
		try:
            #Segurtasun kodea sartu
			segurtasun_kodea = int (input("Sartu segurtasun kodea(5 digitu): "));
            #segurtasun kodea konprobatu
			if(segurtasun_kodea == Xkodea): 					
				kodeOkerra = False;
			else:
				print("Segurtasun-kodea okerra. Saiatu berriro:");
		except ValueError:
			print("segurtasun-kodea okerra. Saiatu berriro:");
    #DUMP komandoa +  segurtasun kodea
	komandoa = "DUMP" + str(segurtasun_kodea);
    #Guztia bidali
	s.sendall(komandoa.encode('ascii'));
    #Erantzuna jaso
	erantzuna = s.recv( mez_tam ).decode('ascii');
	# Erantzuna aztertzen da ("OK" erantzun egokia eta "ER" erantzun okerra beraz, errore kudeaketa)
	if erantzuna[0:2] == "OK":
        #Split-ren bidez banatu datuak eta pantailaratu, Ok eta linea jauzia gabe
		print((erantzuna[3:-2]).split("?"))
		print("Ekintza burututa.");
	elif erantzuna[0:2] == "ER":
		errore = erantzuna[2:]
		# Errore-metodoari deitu dagokion errore-kodearekin.
		try:
			erroreakTratatu(int(errore));
		except ValueError:
			print("Protokolo errore bat egon da1.");
	else:
		print("Protokolo errore bat egon da2.");

#Programa nagusia. Programa izena, zerbitzaria eta portua beharrezkoak dira
if __name__ == "__main__":
	if len( sys.argv ) != 3:
		print( "Erabilera: {} [<zerbitzaria> [<portua>]]".format( sys.argv[0] ))
		exit(2)
	if len( sys.argv ) == 3:
		print( "Zerbitzaria:", sys.argv[1], "IP helbidea:", socket.gethostbyname( sys.argv[1] ) )
		zerb_helb = (sys.argv[1], int(sys.argv[2]));
		s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		s.connect( zerb_helb )

		while True:
			menua();
			#aukera aldagaian gordeko da erabiltzailearen aukera.
			aukera = input();
			# Erabiltzaileak sartutako zenbakiaren arabera, dagokion metodora deituko diogu.
			if aukera == "0":
				s.close();
				exit(0);
			elif aukera == "1":
				eguzkiPlakak(s);
			elif aukera == "2":
				bateriaKargak(s);
			elif aukera == "3":
				propultzailea(s);
			elif aukera == "4":
				sentsoreDatuak(s);
			else: 
				print("Zenbaki desegokia sartu duzu.")
				print("Saiatu berriro:");				
		s.close()

