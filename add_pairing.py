from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

text = layout.read_text()
text = text.replace(
'''            <TextView
                android:id="@+id/statusText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="18dp"
                android:text="Ready."
                android:textColor="@color/accent"
                android:textSize="18sp"
                android:textStyle="bold" />''',
'''            <TextView
                android:id="@+id/pairingCodeText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="18dp"
                android:text=""
                android:textColor="@color/accent"
                android:textSize="34sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/pairingHelpText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp"
                android:text=""
                android:textColor="@color/text_muted"
                android:textSize="15sp" />

            <TextView
                android:id="@+id/statusText"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="18dp"
                android:text="Ready."
                android:textColor="@color/accent"
                android:textSize="18sp"
                android:textStyle="bold" />'''
)
layout.write_text(text)

main.write_text('''package com.scottibyte.multiview.mobile

import android.app.Activity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject
import java.io.BufferedReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : Activity() {
    private val defaultServerUrl = "https://multiview-server.scottibyte.com"
    private val handler = Handler(Looper.getMainLooper())

    private lateinit var serverUrlEdit: EditText
    private lateinit var statusText: TextView
    private lateinit var pairingCodeText: TextView
    private lateinit var pairingHelpText: TextView
    private lateinit var pairButton: Button

    private var pollingCode: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        serverUrlEdit = findViewById(R.id.serverUrlEdit)
        statusText = findViewById(R.id.statusText)
        pairingCodeText = findViewById(R.id.pairingCodeText)
        pairingHelpText = findViewById(R.id.pairingHelpText)
        pairButton = findViewById(R.id.pairButton)

        val savedServer = prefs().getString("serverUrl", defaultServerUrl) ?: defaultServerUrl
        serverUrlEdit.setText(savedServer)

        findViewById<Button>(R.id.saveServerButton).setOnClickListener {
            val value = normalizedServerUrl()
            prefs().edit().putString("serverUrl", value).apply()
            serverUrlEdit.setText(value)
            statusText.text = "Server URL saved."
            Toast.makeText(this, "Server URL saved", Toast.LENGTH_SHORT).show()
        }

        pairButton.setOnClickListener {
            requestPairing()
        }

        val token = prefs().getString("token", null)
        if (!token.isNullOrBlank()) {
            statusText.text = "Stored pairing token found."
        }
    }

    private fun prefs() = getSharedPreferences("multiview_mobile", MODE_PRIVATE)

    private fun normalizedServerUrl(): String {
        return serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
    }

    private fun setBusy(button: Button, busy: Boolean, label: String) {
        button.isEnabled = !busy
        button.text = label
    }

    private fun requestPairing() {
        val serverUrl = normalizedServerUrl()
        prefs().edit().putString("serverUrl", serverUrl).apply()

        pairingCodeText.text = ""
        pairingHelpText.text = ""
        statusText.text = "Requesting pairing code..."
        setBusy(pairButton, true, "Requesting...")

        Thread {
            try {
                val response = httpPostJson(
                    "$serverUrl/api/tv/pairing/request",
                    JSONObject().put("clientName", android.os.Build.MODEL ?: "Android Mobile Client")
                )

                val displayCode = response.optString("displayCode", response.optString("pairingCode"))
                val rawCode = response.optString("pairingCode", displayCode).replace(Regex("\\\\D"), "")

                runOnUiThread {
                    setBusy(pairButton, false, "Pair With Server")
                    pairingCodeText.text = displayCode
                    pairingHelpText.text = "Open MultiView Server → TV Clients → authorize this code."
                    statusText.text = "Waiting for approval..."
                    pollingCode = rawCode
                    pollPairingStatus(rawCode)
                }
            } catch (e: Exception) {
                runOnUiThread {
                    setBusy(pairButton, false, "Pair With Server")
                    statusText.text = "Pairing request failed: ${e.message}"
                }
            }
        }.start()
    }

    private fun pollPairingStatus(code: String) {
        handler.postDelayed({
            if (pollingCode != code) return@postDelayed

            val serverUrl = normalizedServerUrl()

            Thread {
                try {
                    val response = httpGetJson("$serverUrl/api/tv/pairing/status?pairingCode=$code", null)

                    if (response.optBoolean("authorized", false)) {
                        val token = response.optString("token")
                        if (token.isBlank()) {
                            throw RuntimeException("Server approved client but did not return token")
                        }

                        prefs().edit()
                            .putString("serverUrl", serverUrl)
                            .putString("token", token)
                            .apply()

                        pollingCode = null

                        runOnUiThread {
                            pairingCodeText.text = ""
                            pairingHelpText.text = ""
                            statusText.text = "Paired successfully."
                            Toast.makeText(this, "Paired successfully", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        runOnUiThread {
                            statusText.text = "Waiting for approval..."
                            pollPairingStatus(code)
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        statusText.text = "Still waiting or pairing not ready: ${e.message}"
                        pollPairingStatus(code)
                    }
                }
            }.start()
        }, 2500)
    }

    private fun httpGetJson(url: String, bearerToken: String?): JSONObject {
        val conn = URL(url).openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 10000
        conn.readTimeout = 15000
        conn.setRequestProperty("Accept", "application/json")
        if (!bearerToken.isNullOrBlank()) {
            conn.setRequestProperty("Authorization", "Bearer $bearerToken")
        }
        return readJsonResponse(conn)
    }

    private fun httpPostJson(url: String, body: JSONObject): JSONObject {
        val conn = URL(url).openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.connectTimeout = 10000
        conn.readTimeout = 15000
        conn.doOutput = true
        conn.setRequestProperty("Content-Type", "application/json")
        conn.setRequestProperty("Accept", "application/json")

        OutputStreamWriter(conn.outputStream).use { it.write(body.toString()) }

        return readJsonResponse(conn)
    }

    private fun readJsonResponse(conn: HttpURLConnection): JSONObject {
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val text = BufferedReader(stream.reader()).use { it.readText() }

        if (code !in 200..299) {
            throw RuntimeException("HTTP $code: $text")
        }

        return JSONObject(text)
    }
}
''')

print("Added mobile pairing flow.")
