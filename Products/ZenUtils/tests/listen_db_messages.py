import asmqTestDefns
import sys

state = ""
count = 0

def handlerDecorator(fn):
    def handlerfn(msg):
        sys.stderr.write("%s: Received %s\n" % (fn.__name__, msg.body))
        sys.stderr.flush()
        return fn(msg)
    return handlerfn

# comment out this line to log messages to stderr
handlerDecorator = lambda fn : fn

def printout(s):
    sys.stdout.write(s+"\n")
    sys.stdout.flush()

@handlerDecorator
def messageHandler(msg):
    printout( msg.body )

@handlerDecorator
def statusMessageHandler(msg):
    printout( "%d %s" % (count, state))

@handlerDecorator
def initMessageHandler(msg):
    global count
    count = int(msg.body)

@handlerDecorator
def addrecsMessageHandler(msg):
    global count
    count += int(msg.body)

@handlerDecorator
def stateMessageHandler(msg):
    global state
    state = msg.body

@handlerDecorator
def finMessageHandler(msg):
    sys.exit() 

def main():

    consumer = asmqTestDefns.Consumer()
    consumer.register("ADDRECS", addrecsMessageHandler)
    consumer.register("INIT", initMessageHandler)
    consumer.register("STATE", stateMessageHandler)
    consumer.register("STATUS", statusMessageHandler)
    consumer.register("FIN", finMessageHandler)

    printout("ready")

    try:
        consumer.wait()
    except (SystemExit,KeyboardInterrupt):
        consumer.close()
        print "exiting..."
    except Exception as e:
        printout("exiting with error...")
        printout(e)
        raise

if __name__ == "__main__":
    main()
