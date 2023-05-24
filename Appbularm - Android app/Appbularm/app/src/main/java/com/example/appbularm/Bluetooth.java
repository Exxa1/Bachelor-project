package com.example.appbularm;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

// A class to handle Bluetooth connections, listening for incoming data
class MyBluetoothService {
    private final String DebugTAG = "MyBluetoothService";
    private Handler handler; // A handler to interact with the UI thread

    // Constructor
    public MyBluetoothService(BluetoothSocket socket, Handler handler) {
        this.handler = handler;
        // Starts a new thread to handle the Bluetooth connection
        new ConnectedThread(socket).start();
    }

    // Message ID for read messages
    public static final int MESSAGE_READ = 0;

    // Inner class for handling a Bluetooth connection in a separate thread
    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final int INPUT_BYTESIZE = 1024; // The size of our buffer for reading input

        // Constructor for the ConnectedThread class
        public ConnectedThread(BluetoothSocket socket) {
            mmSocket = socket;
            InputStream tmpIn = null;
            // Try to get the input stream from the socket
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                Log.e(DebugTAG, "Error occurred when creating input stream", e);
            }
            mmInStream = tmpIn;
        }

        // The method that runs when the thread starts
        public void run() {
            byte[] mmBuffer = new byte[INPUT_BYTESIZE]; // Buffer for input data
            int byteChar;

            StringBuilder messageBuilder = new StringBuilder();

            // Keep reading the input stream until the thread is interrupted
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    // Read data from the input stream one byte at a time
                    while((byteChar = mmInStream.read()) != -1) {
                        if (byteChar == '\n') {
                            // End of message detected, send message to UI thread
                            String completeMessage = messageBuilder.toString();

                            Message readMsg = handler.obtainMessage(
                                    MESSAGE_READ, completeMessage.length(), -1,
                                    completeMessage.getBytes());
                            readMsg.sendToTarget();

                            // Clear the message builder to start building a new message
                            messageBuilder.setLength(0);
                        } else {
                            // No end of message detected, add byte to message
                            messageBuilder.append((char) byteChar);
                        }
                    }
                } catch (IOException e) {
                    Log.d(DebugTAG, "Input stream was disconnected", e);
                    break;
                }
            }
        }

        // Call this method from the main activity to shut down the connection
        public void cancel() {
            try {
                Thread.currentThread().interrupt();
                mmInStream.close();
                mmSocket.close();
            } catch (IOException e) {
                Log.e(DebugTAG, "Could not close the connect socket", e);
            }
        }
    }
}

// Class for handling messages sent from the MyBluetoothService to the UI thread
class BluetoothHandler extends android.os.Handler {
    private static final int MESSAGE_READ = MyBluetoothService.MESSAGE_READ;
    private final String DebugTAG = "BluetoothHandler";
    private final TextView textViewMessage; // TextView for displaying messages

    // Constructor
    BluetoothHandler(Looper looper, TextView textViewMessage) {
        super(looper);
        this.textViewMessage = textViewMessage;
    }

    // Method for handling incoming messages
    @Override
    public void handleMessage(android.os.Message msg) {
        if (msg.what == MESSAGE_READ) {
            byte[] readBuf = (byte[]) msg.obj;
            String readMessage = new String(readBuf, 0, msg.arg1);
            Log.d(DebugTAG, "Message received: " + readMessage);
            textViewMessage.setText(readMessage); // Display the message in the TextView
        }
    }
}

// Class for handling incoming Bluetooth connections
class AcceptThread extends Thread {
    private final BluetoothServerSocket mmServerSocket;
    private final Handler handler; // Handler for interacting with the UI thread
    private final String DebugTAG = "AcceptThread";
    private static final String NAME = "BLE connection";
    private static final UUID MY_UUID = UUID.fromString("691e69ed-9e3c-48ff-ab87-851d1ef80f47");

    // Constructor
    public AcceptThread(Handler handler) {
        this.handler = handler;
        BluetoothServerSocket tmp = null;
        // Try to get a BluetoothServerSocket for the desired UUID
        try {
            BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
            tmp = bluetoothAdapter.listenUsingRfcommWithServiceRecord(NAME, MY_UUID);
        } catch (IOException e) {
            Log.e(DebugTAG, "Socket's listen() method failed", e);
        }
        mmServerSocket = tmp;
    }

    // The method that runs when the thread starts
    public void run() {
        BluetoothSocket socket = null;
        Log.d(DebugTAG, "starts to listen");
        // Keep listening for incoming connections until the thread is interrupted
        while (!Thread.currentThread().isInterrupted()) {
            try {
                socket = mmServerSocket.accept(); // Wait for an incoming connection
                Log.d(DebugTAG, "Listening!");
            } catch (IOException e) {
                Log.e(DebugTAG, "Socket's accept() method failed", e);
                break;
            }

            if (socket != null) {
                // If a connection was accepted, start a new thread to handle the connection
                Thread.currentThread().interrupt();
                MyBluetoothService myBluetoothService = new MyBluetoothService(socket, handler);
                break;
            }
        }
    }

    // Method for shutting down the thread
    public void cancel() {
        try {
            Thread.currentThread().interrupt();
            mmServerSocket.close();
        } catch (IOException e) {
            Log.e(DebugTAG, "Could not close the connect socket", e);
        }
    }
}
