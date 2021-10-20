import socket, sys, random

# Komandoak berrizendatuko ditugu erabilera errazteko.
class Command:
	Tolestu, Bateria, Propultsatu, Sentsorea= ("FOLD", "BATT", "PROP", "DUMP")

# Ok mezua bidaltzeko.
def sendOK(s, bez_helb, params=0):
	
	if not params == 0:
		s.sendto( ("OK{}\r\n".format( params )).encode(  ),bez_helb )
	else:
		s.sendto( ("OK\r\n").encode(  ),bez_helb )

# Erroreren bat gertatu bada errore mezua bidaltzeko.
def sendER(s, bez_helb, code="0"):
	if not code == "0":
		s.sendto( ("ER{}\r\n".format( code )).encode(  ),bez_helb )
	else:
		s.sendto( ("ER\r\n").encode(  ),bez_helb )

# Hau izango da aukeratutako portua.
PORT = 50069

# saioa azpiprogramaren inplementazioa.
def saioa(s):
	# Parametro finkoen hasieratzea.
	hegalakEgoera = 0 #0 = itxita, 1 = irekita
	bateria = 500
	# While infinitua.
	while True:
		# Mezua eta igorlea jaso
		buf, bez_helb = s.recvfrom(1024)
		# Mezua dekodetu.
		mezua = buf.decode()
		# Simuladorea erabili nahi badugu aurreko agindua komentatu eta aurreko biak deskomentatu.
		#mezua1 = buf.decode()
		#mezua = mezua1[:len(mezua1)-1]
		# Mezurik jaso ez bada hurrengoa jaso.
		if not mezua:
			continue
		# Mezuan jasotakoa aldagaietan banatu.
		komandoa = mezua[0:4]
		segurtasunKodea = mezua[4:9]
		# Komandoa ezezaguna bada, 01 errorea itzuli.
		if komandoa not in ["FOLD", "BATT", "PROP", "DUMP"]:
			sendER(s, bez_helb,"01")
			continue
		# Segurtasun kodea gaizki sartu bada 05 errorea bidali eta hurrengo mezua jaso.
		if segurtasunKodea != "11111":
			sendER(s, bez_helb, "05")
			continue




		# Komandoa FOLD bada hegalak tolestu/destolestu.
		if komandoa == Command.Tolestu:
			# Mezuaren luzera 10-ekoa ez bada errorea bidali. Motza bada 03 errorea, luzea bada 02.
			if len(mezua) < 10:
				sendER(s, bez_helb, "03")
				continue
			if len(mezua) > 10:
				sendER(s, bez_helb, "02")
				continue
			try:
				parametroa = int(mezua[-1])
			except:
				sendER(s, bez_helb, "04")
				continue
			# Saiatu ondorengoa egiten.
			try:
				# Destolesketa eskatzen bada eta hegalak itxita badaude.
				if parametroa==0 and hegalakEgoera == 0: 
					sendOK(s, bez_helb)
					# Egoera aldatu.
					hegalakEgoera = 1
				# Tolesketa eskatzen bada eta hegalak itxita badaude. Ezin da, errore 12 bidali.
				elif parametroa==1 and hegalakEgoera == 0: 
					sendER(s, bez_helb, "12")
				# Tolesketa eskatzen bada eta hegalak irekita badaude.
				elif parametroa==1 and hegalakEgoera == 1:
					sendOK(s, bez_helb)
					# Egoera aldatu.
					hegalakEgoera = 0
				# Destolesketa eskatzen bada eta hegalak irekita badaude. Ezin da, erore 12 bidali.
				elif parametroa==0 and hegalakEgoera == 1: 
					sendER(s, bez_helb, "12")
			# Erroreren bat gertatzen bada, 11 errorea itzuli.
			except:
				sendER(s, bez_helb, "11")
				continue





		# Komandoa BATT bada bateriaren ehunekoa.
		elif komandoa == Command.Bateria:
			# Mezuaren luzera 9-koa ez bada errorea bidali. Motza bada 03 errorea, luzea bada 02.
			if len(mezua) < 9:
				sendER(s, bez_helb, "03")
				continue
			if len(mezua) > 9:
				sendER(s, bez_helb, "02")
				continue
			# Ausazko zenbakia sortu bateriaren egoera aldatu dadin.
			ausaz = random.randint(1,10)
			# Hegalak zabalik baditu bateria kargatuko da.
			if hegalakEgoera == 1:
				# Bateriak ezin izango du 999 baino balio altugo bat eduki.
				if bateria + ausaz <= 999:
					bateria = bateria + ausaz
			# Hegalak destolestuta baditu bateria deskargatuko da.
			else:
				# Eredua sinplifikatzeko bateriaren balio minimoa 100-ekoa izango da.
				if bateria - ausaz >= 100:
					bateria = bateria - ausaz
			# Saiatu bidalketa egiten.
			try:
				sendOK(s, bez_helb, bateria)
			# Erroreren bat gertatzen daba, 21 errorea itzuli.
			except:
				sendER(s, bez_helb, 21)
				continue





		# Komandoa PROP bada propultsatzailea aktibatu.
		elif komandoa == Command.Propultsatu:
			# Mezuaren luzera 13-koa ez bada errorea bidali. Motza bada 03 errorea, luzea bada 02.
			if len(mezua) < 13:
				sendER(s, bez_helb, "03")
				continue
			if len(mezua) > 13:
				sendER(s, bez_helb, "02")
				continue
			# Saiatu.
			try:
				# Propultsatzailearen zenbakia eta iraupena eskuratu.
				zenbakia = int(mezua[9])
				iraupena = int(mezua[10:])
			# Zenbaki osotara pasatzean erroreren bat gertatzen bada, 04 errorea itzuli.
			except:
				sendER(s, bez_helb, "04")
				continue
			# Saiatu.
			try:
				# Iraupena baimendutako baina handiagoa bada, 31 errorea itzuli. Propultsatzaile bakoitzaren iraupen maximoa: zenbakia * 100. 0 zenbakiarena ezik 550-ekoa dela.
				if zenbakia == 0:
					if iraupena > 550:
						sendER(s, bez_helb, "31")
				else:
					if iraupena > 100*zenbakia:
						sendER(s, bez_helb, "31")
			# Erroreren bat gertatzen bada, 32 errorea itzuli.
			except:
				sendER(s, bez_helb, "32")
				continue
			#sendOK(s, bez_helb)




		# Komandoa DUMP bada sentsoreen datuak.
		elif komandoa == Command.Sentsorea:
			# Mezuaren luzera 9-koa ez bada errorea bidali. Motza bada 03 errorea, luzea bada 02.
			if len(mezua) < 9:
				sendER(s, bez_helb, "03")
				continue
			if len(mezua) > 9:
				sendER(s, bez_helb, "02")
				continue
			# Saiatu
			try:
				# Sentsoreen datuen kopurua, ausazko balioa.
				luzera = random.randint(1,5000)
				# Sentsoreen neurketen String-a sortu.
				neurketak = ""
				# Neurketen String-a ausazko zenbakiz bete.
				for i in range(luzera):
					ausazZenbakiak = random.randint(1,99)
					# Galdera ikurren erabilera datuen jasotzea bezeroari errazteko.
					neurketak = neurketak + "?" + str(ausazZenbakiak)
				# Datuak enkodetu.
				neurketak = neurketak.encode()
				# String-aren luzera jaso.
				tamaina = len(neurketak)
				# Sentsoreen datuen lehenengo mila byten bidalketa eta eskaera jaso denaren jakinaraztea.
				s.sendto("OK".encode()+neurketak[:1000]+"\r\n".encode() ,bez_helb )
				# Neurketak eguneratu, lehen mila elementuak kenduz.
				neurketak = neurketak[1000:]
				# Tamaina eguneratu.
				tamaina = tamaina - 1000
				# Tamaina mila baina handiagoa den bitartean, milanaka bidali eta eguneratu. Ok mezurik ez da bidali behar.
				while tamaina > 1000:
					s.sendto(neurketak[:1000]+"\r\n".encode() ,bez_helb )
					neurketak = neurketak[1000:]
					tamaina = tamaina - 1000
				# Azken mezuaren byte kopurua milakoa bada, hau bidali eta ondoren mezu hutsa bidali.
				if tamaina == 1000:
					s.sendto(neurketak[:1000]+"\r\n".encode(), bez_helb)
					hutsa = ""
					hutsa = hutsa.encode()
					s.sendto(hutsa+"\r\n".encode(), bez_helb)
				# Azken mezuaren luzeraren balioa positiboa bada baina mila baina bajuagoa, bidali mezua.
				elif tamaina > 0:
					s.sendto(neurketak+"\r\n".encode(), bez_helb)
			# Erroreren bat gertatzen bada 41 errorea itzuli.
			except:
					sendER(s, bez_helb, 41)
					continue
		# Badaezpadako errore mezua aurreko kasuren batean erori ez bada. Nahiz eta komando ezezagunaren kasua aurretik tratatu den.
		else:
			sendER(s, bez_helb,"01")
			continue

# Programa nagusia.
if __name__ == "__main__":
	# UDP socketa sortu.
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# socketa helbide eta portuarekin erlazionatzeko.
	s.bind( ('', PORT) )
	# While infinitua.
	while True:
		# saioa 	programari deitu saioa hasteko.
		saioa(s)
	# Begiztatik ateratzean socket-a itxi.
	s.close()

