package com.example.appbularm;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Looper;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class MainActivity extends AppCompatActivity {

    private TextView textViewMessage; // TextView to show messages on the screen

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Set the layout defined in 'activity_main'

        textViewMessage = findViewById(R.id.textView_message); // Get reference to the TextView

        // Check if the app has the required permissions, if not request them
        if (!PermissionManager.hasPermissions(this)) {
            PermissionManager.requestPermissions(this);
        } else {
            initBluetooth(); // If permissions are granted, initialize Bluetooth functionality
        }
    }

    private void initBluetooth() {
        // Initialize Bluetooth handler
        BluetoothHandler bluetoothHandler = new BluetoothHandler(Looper.getMainLooper(), textViewMessage);
        // Create a new thread to handle Bluetooth connections
        AcceptThread acceptT = new AcceptThread(bluetoothHandler);
        acceptT.start(); // Start the Bluetooth connection thread
    }

    // This method is called when the user responds to the permission request
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == PermissionManager.PERMISSIONS_REQUEST_CODE) {
            // Check if all permissions are granted
            if (PermissionManager.allPermissionsGranted(grantResults)) {
                initBluetooth(); // If permissions are granted, initialize Bluetooth functionality
            } else {
                // If any permissions are not granted, show a message
                Toast.makeText(this, "Please grant all permissions", Toast.LENGTH_LONG).show();
            }
        } else {
            super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        }
    }
}

class PermissionManager {
    static final int PERMISSIONS_REQUEST_CODE = 1234; // Code to identify the permission request
    // List of permissions that are required
    private static final String[] REQUIRED_PERMISSIONS = {
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_FINE_LOCATION
    };

    // Checks if all required permissions are granted when app started
    static boolean hasPermissions(Context context) {
        for (String permission : REQUIRED_PERMISSIONS) {
            // If any permission is not granted, return false
            if (ContextCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        // If all permissions are granted, return true
        return true;
    }

    // Request for the required permissions
    static void requestPermissions(Activity activity) {
        ActivityCompat.requestPermissions(activity, REQUIRED_PERMISSIONS, PERMISSIONS_REQUEST_CODE);
    }

    // Checks if all requested permissions are granted after asked user to give permissions
    static boolean allPermissionsGranted(int[] grantResults) {
        for (int grantResult : grantResults) {
            // If any permission is not granted, return false
            if (grantResult != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        // If all permissions are granted, return true
        return true;
    }
}
