Prototyping code is proof of concept on how to implement the logic required
in production code.

Checkout the code:

~~~~~
git clone git@github.com:minosg/guardian_angel.git
~~~~~

Compile the protocol

~~~~
cd guardian_angel/protomessage && ./build_protos
~~~~

Go to the protyping folder and generate a raw message on disk

~~~~~
cd ../dev/prototyping/
./create_proto_msg.py msg.raw
~~~~~

If required read the message contents using 

~~~~~
./read_proto_msg.py msg.raw
~~~~~

Test ZeroMQ Comms wth two terminals

~~~~~
./server.py
./client.py msg.raw
~~~~~
