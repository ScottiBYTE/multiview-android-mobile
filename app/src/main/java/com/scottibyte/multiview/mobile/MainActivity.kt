package com.scottibyte.multiview.mobile

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    private val defaultServerUrl = "https://multiview-server.scottibyte.com"

    private lateinit var serverUrlEdit: EditText
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        serverUrlEdit = findViewById(R.id.serverUrlEdit)
        statusText = findViewById(R.id.statusText)

        val savedServer = getPreferences(MODE_PRIVATE)
            .getString("serverUrl", defaultServerUrl) ?: defaultServerUrl

        serverUrlEdit.setText(savedServer)

        findViewById<Button>(R.id.saveServerButton).setOnClickListener {
            val value = serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
            getPreferences(MODE_PRIVATE).edit().putString("serverUrl", value).apply()
            serverUrlEdit.setText(value)
            statusText.text = "Server URL saved."
            Toast.makeText(this, "Server URL saved", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.pairButton).setOnClickListener {
            val value = serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
            statusText.text = "Pairing will use: $value"
        }
    }
}
