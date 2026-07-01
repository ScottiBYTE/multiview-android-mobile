from pathlib import Path

layout = Path("app/src/main/res/layout/activity_main.xml")
main = Path("app/src/main/java/com/scottibyte/multiview/mobile/MainActivity.kt")

text = layout.read_text()

text = text.replace(
'''            <Button
                android:id="@+id/pairButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Pair With Server" />''',
'''            <Button
                android:id="@+id/pairButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Pair With Server" />

            <Button
                android:id="@+id/loadCamerasButton"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="10dp"
                android:text="Load Cameras" />'''
)

text = text.replace(
'''        </LinearLayout>

    </LinearLayout>
</ScrollView>
''',
'''        </LinearLayout>

        <LinearLayout
            android:id="@+id/cameraList"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="18dp"
            android:orientation="vertical" />

    </LinearLayout>
</ScrollView>
'''
)

layout.write_text(text)

kt = main.read_text()

kt = kt.replace(
"import org.json.JSONObject",
"import org.json.JSONArray\nimport org.json.JSONObject"
)

kt = kt.replace(
"import android.widget.Toast",
"import android.widget.LinearLayout\nimport android.widget.Toast"
)

kt = kt.replace(
'''    private lateinit var pairButton: Button''',
'''    private lateinit var pairButton: Button
    private lateinit var cameraList: LinearLayout'''
)

kt = kt.replace(
'''    private var pollingCode: String? = null''',
'''    private var pollingCode: String? = null

    data class Camera(
        val id: String,
        val name: String,
        val group: String,
        val hlsUrl: String,
        val thumbnailUrl: String
    )'''
)

kt = kt.replace(
'''        pairButton = findViewById(R.id.pairButton)''',
'''        pairButton = findViewById(R.id.pairButton)
        cameraList = findViewById(R.id.cameraList)'''
)

kt = kt.replace(
'''        pairButton.setOnClickListener {
            requestPairing()
        }''',
'''        pairButton.setOnClickListener {
            requestPairing()
        }

        findViewById<Button>(R.id.loadCamerasButton).setOnClickListener {
            fetchConfig()
        }'''
)

kt = kt.replace(
'''                            statusText.text = "Paired successfully."
                            Toast.makeText(this, "Paired successfully", Toast.LENGTH_SHORT).show()''',
'''                            statusText.text = "Paired successfully. Loading cameras..."
                            Toast.makeText(this, "Paired successfully", Toast.LENGTH_SHORT).show()
                            fetchConfig()'''
)

insert = r'''
    private fun fetchConfig() {
        val serverUrl = normalizedServerUrl()
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
                    statusText.text = "Loaded ${cameras.size} cameras."
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

    private fun renderCameraList(cameras: List<Camera>) {
        cameraList.removeAllViews()

        if (cameras.isEmpty()) {
            val empty = TextView(this)
            empty.text = "No cameras returned by server."
            empty.setTextColor(android.graphics.Color.rgb(203, 213, 225))
            empty.textSize = 18f
            cameraList.addView(empty)
            return
        }

        cameras.forEach { camera ->
            val card = TextView(this)
            card.text = "${camera.name}\n${camera.group}"
            card.setTextColor(android.graphics.Color.rgb(248, 250, 252))
            card.textSize = 18f
            card.setPadding(22, 18, 22, 18)
            card.setBackgroundColor(android.graphics.Color.rgb(23, 34, 53))

            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            params.setMargins(0, 0, 0, 14)
            cameraList.addView(card, params)
        }
    }

'''

marker = "    private fun httpGetJson"
if "private fun fetchConfig()" not in kt:
    kt = kt.replace(marker, insert + marker)

main.write_text(kt)

print("Added camera config fetch and mobile camera list.")
