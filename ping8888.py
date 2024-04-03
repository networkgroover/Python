from EapiClientLib import EapiClient
import time

switch = EapiClient( disableAaa=True, privLevel=15 )
i = 0

while i < 1:
   response = switch.runCmds( 1, ['ping 77.77.77.77','ping 88.88.88.88','ping 99.99.99.99'] )
   time.sleep(5)
   print('PING!')
#print 'The switch's system MAC addess is', response['result'][0]['systemMacAddress']