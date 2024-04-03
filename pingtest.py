from EapiClientLib import EapiClient
import time

switch = EapiClient( disableAaa=True, privLevel=15 )
LOOP_COUNTER = 1

while True:
    try:
        print("LOOP RUN: ", LOOP_COUNTER)
        print("Ctrl-C to exit")
        response = switch.runCmds( 1, ['ping 77.77.77.77','ping 88.88.88.88','ping 99.99.99.99'] )
        time.sleep(5)
        LOOP_COUNTER +=1

    except KeyboardInterrupt:
        print("Script interrupted by user")
        break