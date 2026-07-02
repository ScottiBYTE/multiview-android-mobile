package com.scottibyte.multiview.mobile

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.media3.common.MediaItem
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.ui.PlayerView
import androidx.recyclerview.widget.RecyclerView
import coil.load
import org.json.JSONArray
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
    private lateinit var connectionSummaryText: TextView
    private lateinit var cameraHeaderText: TextView
    private lateinit var connectionDetails: View
    private lateinit var connectionToggleButton: Button
    private lateinit var reorderButton: Button
    private lateinit var connectionStateText: TextView
    private lateinit var pairingCodeText: TextView
    private lateinit var pairingHelpText: TextView
    private lateinit var pairButton: Button
    private lateinit var cameraRecycler: RecyclerView
    private lateinit var cameraAdapter: CameraAdapter
    private var editMode = false

    private var pollingCode: String? = null

    data class Camera(
        val id: String,
        val name: String,
        val group: String,
        val hlsUrl: String,
        val thumbnailUrl: String
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        serverUrlEdit = findViewById(R.id.serverUrlEdit)
        statusText = findViewById(R.id.statusText)
        connectionSummaryText = findViewById(R.id.connectionSummaryText)
        cameraHeaderText = findViewById(R.id.cameraHeaderText)
        connectionDetails = findViewById(R.id.connectionDetails)
        connectionToggleButton = findViewById(R.id.connectionToggleButton)
        reorderButton = findViewById(R.id.reorderButton)
        connectionStateText = findViewById(R.id.connectionStateText)
        pairingCodeText = findViewById(R.id.pairingCodeText)
        pairingHelpText = findViewById(R.id.pairingHelpText)
        pairButton = findViewById(R.id.pairButton)
        cameraRecycler = findViewById(R.id.cameraRecycler)
        cameraAdapter = CameraAdapter()
        cameraRecycler.layoutManager = LinearLayoutManager(this)
        cameraRecycler.adapter = cameraAdapter

        ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
            ItemTouchHelper.UP or ItemTouchHelper.DOWN,
            0
        ) {
            override fun isLongPressDragEnabled(): Boolean = editMode

            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ): Boolean {
                return cameraAdapter.moveItem(viewHolder.bindingAdapterPosition, target.bindingAdapterPosition)
            }

            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {}

            override fun clearView(recyclerView: RecyclerView, viewHolder: RecyclerView.ViewHolder) {
                super.clearView(recyclerView, viewHolder)
                saveCameraOrder(cameraAdapter.currentIds())
            }
        }).attachToRecyclerView(cameraRecycler)

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
            if (prefs().getString("token", null).isNullOrBlank()) {
                requestPairing()
            } else {
                resetPairing()
            }
        }

        findViewById<TextView>(R.id.titleText).setOnLongClickListener {
            toggleEditMode()
            true
        }

        connectionToggleButton.setOnLongClickListener {
            toggleEditMode()
            true
        }

        reorderButton.setOnClickListener {
            toggleEditMode()
            reorderButton.text = if (editMode) "Done" else "Sort"
        }

        connectionToggleButton.setOnClickListener {
            connectionDetails.visibility = if (connectionDetails.visibility == View.VISIBLE) {
                View.GONE
            } else {
                View.VISIBLE
            }
        }


        val token = prefs().getString("token", null)
        if (!token.isNullOrBlank()) {
            connectionSummaryText.text = "Camera viewer"
            connectionStateText.text = "Connection status: Connected"
            connectionDetails.visibility = View.GONE
            pairButton.text = "Reset Pairing"
            statusText.text = "Stored pairing token found. Loading cameras..."
            fetchConfig()
        } else {
            connectionSummaryText.text = "Camera viewer"
            connectionStateText.text = "Connection status: Not paired"
            connectionDetails.visibility = View.VISIBLE
            pairButton.text = "Pair With Server"
        }
    }

    private fun prefs() = getSharedPreferences("multiview_mobile", MODE_PRIVATE)

    private fun normalizedServerUrl(): String {
        return serverUrlEdit.text.toString().trim().trimEnd('/').ifBlank { defaultServerUrl }
    }

    private fun savedServerUrl(): String {
        return prefs()
            .getString("serverUrl", null)
            ?.trim()
            ?.trimEnd('/')
            ?.ifBlank { defaultServerUrl }
            ?: defaultServerUrl
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
                val rawCode = response.optString("pairingCode", displayCode).replace(Regex("\\D"), "")

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
                            connectionSummaryText.text = "Camera viewer"
                            connectionStateText.text = "Connection status: Connected"
                            connectionDetails.visibility = View.GONE
                            pairButton.text = "Reset Pairing"
                            statusText.text = "Paired successfully. Loading cameras..."
                            Toast.makeText(this, "Paired successfully", Toast.LENGTH_SHORT).show()
                            fetchConfig()
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



    private fun resetPairing() {
        pollingCode = null
        prefs().edit().remove("token").apply()
        pairButton.text = "Pair With Server"
        connectionStateText.text = "Connection status: Not paired"
        connectionDetails.visibility = View.VISIBLE
        cameraAdapter.submit(emptyList())
        cameraHeaderText.text = "Cameras"
        statusText.text = "Pairing reset. Pair with the server again."
        Toast.makeText(this, "Pairing reset", Toast.LENGTH_SHORT).show()
    }

    private fun fetchConfig() {
        val serverUrl = savedServerUrl()
        serverUrlEdit.setText(serverUrl)
        val token = prefs().getString("token", null)

        if (token.isNullOrBlank()) {
            statusText.text = "No token stored. Pair with the server first."
            return
        }

        statusText.text = "Loading camera configuration..."

        Thread {
            try {
                val response = httpGetJson("$serverUrl/api/tv/config", token)
                val cameras = parseCameras(response)

                runOnUiThread {
                    renderCameraList(cameras)
                    cameraHeaderText.text = "Cameras (${cameras.size})"
                    connectionStateText.text = "Connection status: Connected • ${cameras.size} cameras"
                    statusText.visibility = View.GONE
                }
            } catch (e: Exception) {
                runOnUiThread {
                    statusText.text = "Failed to load cameras: ${e.message}"
                }
            }
        }.start()
    }

    private fun parseCameras(root: JSONObject): List<Camera> {
        val arr: JSONArray = root.optJSONArray("cameras")
            ?: root.optJSONObject("config")?.optJSONArray("cameras")
            ?: JSONArray()

        val result = mutableListOf<Camera>()

        for (i in 0 until arr.length()) {
            val item = arr.optJSONObject(i) ?: continue

            val id = item.optString("id")
            val name = item.optString("name", id)
            val group = item.optString("group", "Default")
            val streams = item.optJSONObject("streams")
            val images = item.optJSONObject("images")
            val hlsUrl = item.optString(
                "hlsUrl",
                streams?.optString("hls") ?: item.optString(
                    "url",
                    item.optString("streamUrl", "")
                )
            )
            val thumbnailUrl = images?.optString("thumbnail") ?: ""

            if (id.isNotBlank() && hlsUrl.isNotBlank()) {
                result.add(Camera(id, name, group, hlsUrl, thumbnailUrl))
            }
        }

        return result.sortedWith(compareBy<Camera> { it.group }.thenBy { it.name })
    }

    private fun orderedCameras(cameras: List<Camera>): List<Camera> {
        val saved = prefs().getString("cameraOrder", "") ?: ""
        val ids = saved.split(",").filter { it.isNotBlank() }
        if (ids.isEmpty()) return cameras

        val byId = cameras.associateBy { it.id }
        val ordered = ids.mapNotNull { byId[it] }
        val newCameras = cameras.filterNot { ids.contains(it.id) }
        return ordered + newCameras
    }

    private fun saveCameraOrder(ids: List<String>) {
        prefs().edit().putString("cameraOrder", ids.joinToString(",")).apply()
    }

    private fun toggleEditMode() {
        editMode = !editMode
        cameraAdapter.setEditMode(editMode)
        statusText.visibility = View.VISIBLE
        statusText.text = if (editMode) {
            "Edit mode: long-press and drag cameras to reorder."
        } else {
            "Camera order saved."
        }
    }

    private fun renderCameraList(cameras: List<Camera>) {
        cameraAdapter.submit(orderedCameras(cameras))
    }

    inner class CameraAdapter : RecyclerView.Adapter<CameraAdapter.CameraViewHolder>() {
        private val items = mutableListOf<Camera>()
        private var adapterEditMode = false
        private var previewPlayer: ExoPlayer? = null
        private var previewCameraId: String? = null

        fun submit(cameras: List<Camera>) {
            items.clear()
            items.addAll(cameras)
            notifyDataSetChanged()
        }

        fun setEditMode(enabled: Boolean) {
            adapterEditMode = enabled
            notifyDataSetChanged()
        }

        fun currentIds(): List<String> = items.map { it.id }

        fun moveItem(from: Int, to: Int): Boolean {
            if (from == RecyclerView.NO_POSITION || to == RecyclerView.NO_POSITION) return false
            if (from !in items.indices || to !in items.indices) return false
            val item = items.removeAt(from)
            items.add(to, item)
            notifyItemMoved(from, to)
            return true
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CameraViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_camera_card, parent, false)
            return CameraViewHolder(view)
        }

        override fun onBindViewHolder(holder: CameraViewHolder, position: Int) {
            val camera = items[position]
            holder.name.text = camera.name
            holder.group.text = camera.group.ifBlank { "Default" }
            holder.dragHandle.visibility = if (adapterEditMode) View.VISIBLE else View.GONE
            val previewActive = previewCameraId == camera.id
            holder.inlinePlayer.visibility = if (previewActive) View.VISIBLE else View.GONE
            holder.thumbnail.visibility = if (previewActive) View.GONE else View.VISIBLE
            holder.placeholder.visibility = View.GONE
            holder.state.text = if (previewActive) "LIVE" else "●"

            if (previewActive) {
                startPreview(camera, holder.inlinePlayer)
            }

            if (!previewActive && camera.thumbnailUrl.isNotBlank()) {
                holder.thumbnail.load(camera.thumbnailUrl) {
                    crossfade(true)
                    listener(
                        onSuccess = { _, _ ->
                            holder.placeholder.visibility = View.GONE
                        },
                        onError = { _, _ ->
                            holder.placeholder.visibility = View.VISIBLE
                        }
                    )
                }
            } else {
                holder.thumbnail.setImageDrawable(null)
                holder.placeholder.visibility = View.VISIBLE
            }

            holder.itemView.setOnClickListener {
                if (adapterEditMode) return@setOnClickListener

                val index = items.indexOfFirst { it.id == camera.id }

                if (previewCameraId == camera.id) {
                    val intent = Intent(this@MainActivity, PlayerActivity::class.java)
                        .putExtra("cameraIndex", index)
                        .putStringArrayListExtra("cameraNames", ArrayList(items.map { it.name }))
                        .putStringArrayListExtra("cameraGroups", ArrayList(items.map { it.group }))
                        .putStringArrayListExtra("cameraUrls", ArrayList(items.map { it.hlsUrl }))

                    startActivity(intent)
                } else {
                    stopPreview()
                    previewCameraId = camera.id
                    notifyDataSetChanged()
                }
            }
        }


        private fun makePreviewPlayer(): ExoPlayer {
            val httpDataSourceFactory = DefaultHttpDataSource.Factory()
            val mediaSourceFactory = DefaultMediaSourceFactory(this@MainActivity)
                .setDataSourceFactory(httpDataSourceFactory)

            return ExoPlayer.Builder(this@MainActivity)
                .setMediaSourceFactory(mediaSourceFactory)
                .build()
        }

        private fun startPreview(camera: Camera, view: PlayerView) {
            if (previewPlayer == null) {
                previewPlayer = makePreviewPlayer()
            }

            view.player = previewPlayer
            previewPlayer?.setMediaItem(MediaItem.fromUri(camera.hlsUrl))
            previewPlayer?.prepare()
            previewPlayer?.playWhenReady = true
        }

        private fun stopPreview() {
            previewPlayer?.release()
            previewPlayer = null
            previewCameraId = null
        }

        override fun onViewRecycled(holder: CameraViewHolder) {
            super.onViewRecycled(holder)
            if (holder.inlinePlayer.player == previewPlayer) {
                holder.inlinePlayer.player = null
            }
        }

        override fun getItemCount(): Int = items.size

        inner class CameraViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val name: TextView = view.findViewById(R.id.cameraName)
            val group: TextView = view.findViewById(R.id.cameraGroup)
            val dragHandle: TextView = view.findViewById(R.id.dragHandle)
            val thumbnail: ImageView = view.findViewById(R.id.cameraThumb)
            val inlinePlayer: PlayerView = view.findViewById(R.id.inlinePlayer)
            val placeholder: TextView = view.findViewById(R.id.thumbPlaceholder)
            val state: TextView = view.findViewById(R.id.cameraState)
        }
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
